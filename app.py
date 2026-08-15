from flask import Flask, render_template_string, request, jsonify, Response
import yt_dlp
import requests

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>High-Speed Downloader</title>
    <style>
        body { background: #0b0f19; color: white; font-family: Arial, sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .box { background: #151c2c; padding: 25px; border-radius: 12px; width: 100%; max-width: 480px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); text-align: center; }
        h1 { color: #38bdf8; font-size: 22px; margin-bottom: 5px; }
        p { color: #94a3b8; font-size: 13px; margin-bottom: 20px; }
        .input-group { display: flex; gap: 8px; margin-bottom: 15px; }
        input { flex: 1; padding: 12px; border-radius: 8px; border: 1px solid #334155; background: #0f172a; color: white; outline: none; }
        input:focus { border-color: #38bdf8; }
        .btn { background: #2563eb; color: white; border: none; padding: 12px 20px; border-radius: 8px; font-weight: bold; cursor: pointer; width: 100%; transition: background 0.2s; }
        .btn:hover { background: #1d4ed8; }
        #result { margin-top: 15px; text-align: left; }
        .q-card { background: #1e293b; padding: 12px; border-radius: 8px; margin-top: 10px; display: flex; justify-content: space-between; align-items: center; }
        .dl-btn { background: #22c55e; color: white; padding: 8px 14px; border-radius: 6px; text-decoration: none; font-size: 14px; font-weight: bold; }
        .dl-btn:hover { background: #16a34a; }
        .error { color: #ef4444; font-size: 14px; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="box">
        <h1>🎬 High-Speed Downloader</h1>
        <p>Instagram Reels, YouTube HD Videos & Songs</p>
        <div class="input-group">
            <input type="text" id="urlInput" placeholder="Paste Link Here...">
        </div>
        <button class="btn" onclick="fetchMedia()">Fetch Download Links</button>
        <div id="result"></div>
    </div>

    <script>
        async function fetchMedia() {
            const url = document.getElementById('urlInput').value;
            const resultDiv = document.getElementById('result');
            if (!url) {
                resultDiv.innerHTML = '<div class="error">Please enter a valid link!</div>';
                return;
            }
            resultDiv.innerHTML = '<p style="color:#f59e0b;">⏳ Fetching download links...</p>';
            
            try {
                const res = await fetch('/fetch', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url: url })
                });
                const data = await res.json();
                if (res.ok) {
                    let html = `<h4 style="color:#38bdf8; font-size:14px; margin-bottom:8px;">${data.title}</h4>`;
                    data.formats.forEach(f => {
                        const dlLink = `/proxy_download?url=${encodeURIComponent(f.url)}&filename=${encodeURIComponent(data.title + '.mp4')}`;
                        html += `<div class="q-card"><span>🎥 HD Video</span><a href="${dlLink}" class="dl-btn" target="_blank">Download</a></div>`;
                    });
                    resultDiv.innerHTML = html;
                } else {
                    resultDiv.innerHTML = `<div class="error">${data.error || 'Failed to fetch video.'}</div>`;
                }
            } catch (e) {
                resultDiv.innerHTML = '<div class="error">Network error occurred!</div>';
            }
        }
    </script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route("/fetch", methods=["POST"])
def fetch_media():
    data = request.json
    video_url = data.get("url")
    if not video_url:
        return jsonify({"error": "No URL provided"}), 400
    
    ydl_opts = {
        'quiet': True,
        'format': 'best',
        'noplaylist': True,
        'extractor_args': {'youtube': {'player_client': ['android', 'web']}}
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            title = info.get('title', 'video')
            download_url = info.get('url') or (info.get('formats')[-1]['url'] if info.get('formats') else None)
            
            if not download_url:
                return jsonify({"error": "Could not extract direct stream URL."}), 400
            
            formats_list = [{'url': download_url}]
            return jsonify({"title": title, "formats": formats_list})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/proxy_download")
def proxy_download():
    media_url = request.args.get("url")
    filename = request.args.get("filename", "video.mp4")
    if not media_url:
        return "Missing URL", 400
    try:
        req = requests.get(media_url, stream=True, timeout=30)
        return Response(req.iter_content(chunk_size=1024*1024), headers={
            'Content-Disposition': f'attachment; filename="{filename}"',
            'Content-Type': req.headers.get('content-type', 'video/mp4')
        })
    except Exception as e:
        return str(e), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
    
