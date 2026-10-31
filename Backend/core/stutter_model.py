import subprocess

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from transformers import Wav2Vec2Model

SR = 16000


class TemporalCNNv2(nn.Module):          # layer names match the trained model
    def __init__(self, in_dim=1536, hidden=128, num_classes=3, n_conv=2):
        super().__init__()
        self.norm = nn.LayerNorm(in_dim)
        convs = [nn.Conv1d(in_dim, hidden, kernel_size=5, padding=2)]
        for _ in range(n_conv - 1):
            convs.append(nn.Conv1d(hidden, hidden, kernel_size=5, padding=2))
        self.convs = nn.ModuleList(convs)
        self.dropout = nn.Dropout(0.3)
        self.fc = nn.Linear(hidden * 2, num_classes)

    def forward(self, x):
        x = self.norm(x).transpose(1, 2)
        for conv in self.convs:
            x = F.relu(conv(x))
        x = torch.cat([x.max(dim=2).values, x.mean(dim=2)], dim=1)
        return self.fc(self.dropout(x))


def load_audio(path):
    # ffmpeg decode (handles mp4/webm/wav) to 16 kHz mono float32
    cmd = ["ffmpeg", "-nostdin", "-threads", "0", "-i", path,
           "-f", "s16le", "-ac", "1", "-acodec", "pcm_s16le", "-ar", str(SR), "-"]
    out = subprocess.run(cmd, capture_output=True, check=True).stdout
    return torch.from_numpy(np.frombuffer(out, np.int16).astype(np.float32) / 32768.0)


def window_starts(n_samples, window, hop):
    if n_samples <= window:
        return [0]
    starts = list(range(0, n_samples - window + 1, hop))
    if starts[-1] + window < n_samples:
        starts.append(n_samples - window)          # last window ends at the end of the recording
    return starts


def union_seconds(intervals):
    total, cur_s, cur_e = 0.0, None, None
    for s, e in sorted(intervals):
        if cur_e is None or s > cur_e:
            if cur_e is not None:
                total += cur_e - cur_s
            cur_s, cur_e = s, e
        else:
            cur_e = max(cur_e, e)
    if cur_e is not None:
        total += cur_e - cur_s
    return total


def merge_segments(idx, spans, scores):
    segs = []
    for k in idx:
        s, e = spans[k]
        if segs and k - segs[-1]["last"] == 1:
            g = segs[-1]
            g["end"], g["last"] = e, k
            g["scores"].append(float(scores[k]))
        else:
            segs.append({"start": s, "end": e, "last": k, "scores": [float(scores[k])]})
    return [{"start": round(g["start"], 2), "end": round(g["end"], 2),
             "seconds": round(g["end"] - g["start"], 2), "windows": len(g["scores"]),
             "max_score": round(max(g["scores"]), 3),
             "mean_score": round(float(np.mean(g["scores"])), 3)} for g in segs]


class StutterDetector:
    def __init__(self, model_path, device=None):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        try:
            cfg = torch.load(model_path, map_location="cpu")
        except Exception:
            cfg = torch.load(model_path, map_location="cpu", weights_only=False)
        self.names = cfg["class_names"]
        self.thresholds = np.array(cfg["thresholds"])
        self.layers = cfg["layers"]
        self.window = cfg["window_samples"]
        self.pool_kernel = cfg.get("pool_kernel", 2)
        self.w2v = Wav2Vec2Model.from_pretrained(cfg["backbone"]).to(self.device).eval()
        self.nets = []
        for state in cfg["state_dicts"]:
            net = TemporalCNNv2(in_dim=cfg["in_dim"], hidden=cfg["hidden"],
                                num_classes=cfg["num_classes"], n_conv=cfg["n_conv"])
            net.load_state_dict(state)
            self.nets.append(net.to(self.device).eval())

    @torch.no_grad()
    def _predict(self, chunks, batch_size=4):
        out = []
        use_amp = self.device == "cuda"
        for i in range(0, len(chunks), batch_size):
            x = torch.stack(chunks[i:i + batch_size]).to(self.device)
            with torch.autocast("cuda", dtype=torch.float16, enabled=use_amp):
                hs = self.w2v(x, output_hidden_states=True).hidden_states
            feats = []
            for L in self.layers:
                h = hs[L].float()                                                          # [B, 149, 768]
                h = F.avg_pool1d(h.transpose(1, 2), kernel_size=self.pool_kernel).transpose(1, 2)
                feats.append(F.layer_norm(h, h.shape[-1:]))                               # same as training
            f = torch.cat(feats, dim=-1)                                                   # [B, 74, 1536]
            p = torch.stack([torch.sigmoid(n(f)) for n in self.nets]).mean(0)
            out.append(p.cpu())
        return torch.cat(out).numpy()

    def analyze(self, path, hop_seconds=3.0):
        wav = load_audio(path)
        n = len(wav)
        if n < SR // 2:
            raise ValueError("Recording is too short (under 0.5 s).")
        duration = n / SR
        win = self.window

        starts = window_starts(n, win, int(hop_seconds * SR))
        chunks = []
        for s in starts:
            c = wav[s:s + win]
            c = (c - c.mean()) / (c.std() + 1e-7)          # normalize BEFORE padding, as in training
            if len(c) < win:
                c = F.pad(c, (0, win - len(c)))
            chunks.append(c)

        probs = self._predict(chunks)
        flags = probs > self.thresholds
        spans = [(s / SR, min((s + win) / SR, duration)) for s in starts]

        types = {}
        for j, name in enumerate(self.names):
            idx = np.where(flags[:, j])[0]
            segs = merge_segments(idx, spans, probs[:, j])
            types[name] = {
                "threshold": float(self.thresholds[j]),
                "windows_flagged": int(len(idx)),
                "num_segments": len(segs),
                "seconds_flagged": round(union_seconds([spans[k] for k in idx]), 2),
                "max_score": round(float(probs[idx, j].max()), 3) if len(idx) else None,
                "mean_score": round(float(probs[idx, j].mean()), 3) if len(idx) else None,
                "segments": segs,
            }

        any_idx = np.where(flags.any(axis=1))[0]
        secs_any = union_seconds([spans[k] for k in any_idx])
        timeline = [{
            "start": round(spans[k][0], 2), "end": round(spans[k][1], 2),
            "scores": {nm: round(float(probs[k, j]), 3) for j, nm in enumerate(self.names)},
            "flagged": [nm for j, nm in enumerate(self.names) if flags[k, j]],
        } for k in range(len(starts))]

        return {
            "file": str(path), "duration_s": round(duration, 2),
            "window_s": win / SR, "hop_s": hop_seconds,
            "windows_analyzed": len(starts),
            "windows_with_any_flag": int(len(any_idx)),
            "seconds_with_any_flag": round(secs_any, 2),
            "share_of_recording_flagged": round(secs_any / duration, 3),
            "types": types, "timeline": timeline,
        }
