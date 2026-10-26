# Local smoothing test 09 — 2026-10-26

The owner likes the fresh 24-cel snow-white test 07, but finds it slightly choppy and requests polish. Most moving cels were held three frames at 24 fps, producing eight pose changes per second. Keep the original version intact.

A first, local DIS bidirectional flow experiment (08) was rendered and rejected after inspection: broken/occluded paw edges and inconsistent motion correspondence. It is not the delivered smoothing candidate. The replacement was first tested on three key transitions (head turn, paw lift, paw lower), then rendered through the active movement using a pinned RIFE v4.9 ONNX model on CPU.

The delivered 09 has 24 source drawings and 41 calculated intermediate video frames. Do not call the latter additional hand-drawn cels. The original 24 key-pose RGB arrays, all six original blink frames and the final 21-frame pause are preserved before lossy encoding. The first pause is nine frames rather than twelve, to ease into movement. Total remains 96 output frames / 24 fps / four seconds. All 41 derived full-body frames and paw-detail thumbnails were visually inspected; no full realtime playback claim. Residual source detail/model drift remains and user review determines whether the result is better.

Verified 24 endpoint equalities, preserved hold/blink equalities, all 96 encoded timestamps against n/24, complete video decode, original-source SHA hashes, and valid package-relative source-sheet paths. A side-by-side original/smoothing comparison was also encoded and fully decoded. Pixel equalities refer to pre-encode arrays, not H.264-decoded RGB.

`studio/smooth_luna_rife.py` reproduces the result from the 07 package and separately supplied model. Model SHA-256: `76e4cef9ab42fa7dd4e8f6e4aba47462051e3faa969e4bca6479784fbab0ac6f`. Pinned mirror: https://huggingface.co/edgetools/rife/resolve/321b593c5f36c26f5b08fa2838dcf5eece382fa0/rife49.onnx . Primary upstream: https://github.com/hzwer/Practical-RIFE . Export: https://huggingface.co/yuvraj108c/rife-onnx . MIT license and export model card accompany the review package. ONNX Runtime telemetry opt-out is applied before import and again at runtime; no network audit is claimed.

Saved candidate video, comparison, 24 source drawings, 41 derived PNGs, audit and licenses: https://chatgpt.com/library?file_id=libfile_3aa2bf9930248191849224e7d76282a8&account_id=personal
