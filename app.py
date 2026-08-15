from flask import Flask, render_template_string, request, jsonify, Response
import yt_dlp, requests

app = Flask(__name__)

# Adsterra / Monetag Script tag paste karein
AD_CODE = """"""

html_code = """
<!DOCTYPE html>
<html>
<head>
    <title>All-in-One Downloader</title>
    """ + AD_CODE + """
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { background: #0b0f19; color: white; text-align: center; font-family: sans-serif; padding: 15px; margin: 0; }
        .box { background: #151c2c; max-width: 480px; margin: 10px auto; padding: 20px; border-radius: 16px; border: 1px solid #232f48; }
        h1 { color: #38bdf8; font-size: 20px; margin-bottom: 5px; }
        p { color: #94a3b8; font-size: 12px; margin-bottom: 15px; }
        .input-group { display: flex; gap: 8px; justify-content: center; margin-bottom: 10px; }
        input { flex: 1; padding: 12px; border-radius: 8px; border: 1px solid #334155; background: #0b0f19; color: white; font-size: 14px; outline: none; }
        .btn { background: linear-gradient(45deg, #2563eb, #3b82f6); color: white; border: none; padding: 12px; border-radius: 8px; font-weight: bold; font-size: 15px; cursor: pointer; width: 100%; }
        #result { margin-top: 15px; text-align: center; }
        .q-card { background: #1e293b; padding: 10px 14px; margin-top: 10px; border-radius: 10px; border: 1px solid #334155; display: flex; justify-content: space-between; align-items: center; }
        .dl-btn { background: #22c55e; color: white; padding: 8px 12px; border-radius: 6px; text-decoration: none; font-weight: bold; font-size: 12px; }
    </style>
</head>
<body>
    <div class="box">
        <h1>🎬 High-Speed Downloader</h1>
        <p>Instagram Reels, YouTube HD Videos & DJ Songs</p>
        <div class="input-group">
            <input type="text" id="videoUrl" placeholder="Paste Link Here...">
        </div>
        <button class="btn" onclick="fetchMedia()">Fetch Download Links</button>
        <div id="result"></div>
    </div>
    <script>
        async function fetchMedia() {
            const url = document.getElementById('videoUrl').value.trim();
            const resultDiv = document.getElementById('result');
            if(!url) { alert("Link Paste Karein!"); return; }
            resultDiv.innerHTML = "<p style='color:#f59e0b;'>⏳ Extracting Link...</p>";
            try {
                const res = await fetch('/fetch', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ url: url }) });
                const data = await res.json();
                if(res.ok) {
                    let html = `<h4 style="color:#f87171; font-size:13px;">${data.title}</h4>`;
                    data.formats.forEach(f => {
                        const dlLink = `/proxy_download?url=${encodeURIComponent(f.url)}&filename=${encodeURIComponent(data.title + '.mp4')}`;
                        html += `<div class="q-card"><div><b>📹 ${f.quality}</b></div><a href="${dlLink}" class="dl-btn">📥 Download</a></div>`;
                    });
                    resultDiv.innerHTML = html;
                } else { resultDiv.innerHTML = `<p style="color:#ef4444;">❌ Error!</p>`; }
            } catch(e) { resultDiv.innerHTML = `<p style="color:#ef4444;">❌ Server Error!</p>`; }
        }
    </script>
</body>
</html>
"""

@app.route("/")
def home(): return render_template_string(html_code)

@app.route("/fetch", methods=["POST"])
def fetch():
    video_url = request.json.get("url")
    ydl_opts = {'quiet': True, 'format': 'best'}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            title = info.get('title', 'Video')
            formats_list = [{'quality': 'HD Video', 'url': info.get('url')}]
            return jsonify({"title": title, "formats": formats_list})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/proxy_download")
def proxy_download():
    media_url = request.args.get("url")
    filename = request.args.get("filename", "video.mp4")
    req = requests.get(media_url, stream=True)
    return Response(req.iter_content(chunk_size=1024*1024), headers={'Content-Disposition': f'attachment; filename="{filename}"'})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
