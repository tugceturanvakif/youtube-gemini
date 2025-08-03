# gemini_server.py - Google Gemini API ile YouTube özetleyici
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import re
import requests


# GEMINI API KEY'İNİ BURAYA YAZ
GEMINI_API_KEY = "AIzaSyCC26sECnkOcgEpXd8ZuAsTGVU_0xpQ8ow"

class GeminiHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            try:
                with open('index.html', 'r', encoding='utf-8') as f:
                    self.wfile.write(f.read().encode('utf-8'))
            except:
                self.wfile.write(b"index.html yok!")
    
    def do_POST(self):
        if self.path == '/api/summarize':
            try:
                self.send_response(200)
                self.send_header('Content-type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                self.end_headers()

                # Video URL al
                content_length = int(self.headers['Content-Length'])
                data = json.loads(self.rfile.read(content_length).decode('utf-8'))
                video_url = data.get('videoUrl')
                
                # Video ID çıkar
                video_id = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11})', video_url).group(1)
                print(f"✅ Video ID: {video_id}")
                
                # Test için örnek transcript (gerçek YouTube API sorunu çözülene kadar)
                test_transcript = """
                Bugün Türkiye'de önemli ekonomik gelişmeler yaşandı. Cumhurbaşkanı yaptığı açıklamada, 
                yeni dönemde uygulanacak ekonomi politikalarını detaylandırdı. Enflasyonla mücadelede 
                kararlılıkla devam edileceği belirtildi. Merkez Bankası faiz politikalarını gözden geçirecek. 
                Yatırım teşvikleri artırılacak ve ihracat hedefleri yükseltildi. Turizm sektörüne özel 
                destek sağlanacak. Teknoloji yatırımları öncelik olacak. Gençlerin istihdamı için özel 
                programlar başlatılacak. Asgari ücret artışı açıklandı. KDV indirimleri uzatıldı.
                Emlak sektöründe yeni düzenlemeler yapıldı. Tarım destekleri artırıldı.
                """
                
                print("🧪 TEST MODU: Örnek transcript kullanılıyor")
                print(f"📄 Transcript uzunluğu: {len(test_transcript)} karakter")
                
                # Gemini ile özet yap
                summary = self.gemini_ozet_yap(test_transcript)
                
                response = {
                    'success': True,
                    'title': 'Test Video - Ekonomi Haberleri',
                    'channel': 'Test Kanal',
                    'thumbnail': f"https://img.youtube.com/vi/{video_id}/mqdefault.jpg",
                    'summary': summary
                }
                
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                
            except Exception as e:
                print(f"❌ Hata: {e}")
                error = {'success': False, 'error': str(e)}
                self.wfile.write(json.dumps(error, ensure_ascii=False).encode('utf-8'))
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def gemini_ozet_yap(self, transcript):
        """Google Gemini ile özet yap"""
        print("🤖 Gemini API'ye istek gönderiliyor...")
        
        if GEMINI_API_KEY == "your-gemini-api-key-here":
            return "⚠️ Gemini API key gerekli! Lütfen dosyada API key'inizi güncelleyin."
        
        # Gemini API endpoint - Güncel model ismi
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        
        # Request data
        data = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": f"""Bu video metnini Türkçe olarak özetle. Özet şu şekilde olsun:

- 3-4 paragraf halinde
- Ana noktaları içeren
- Net ve anlaşılır
- Türkçe dilinde
- Önemli detayları kaçırmayan

Video metni:
{transcript}"""
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.7,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 1024,
            }
        }
        
        try:
            response = requests.post(url, json=data, timeout=60)
            
            print(f"📊 Gemini API Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                
                # Gemini response yapısını kontrol et
                if 'candidates' in result and len(result['candidates']) > 0:
                    if 'content' in result['candidates'][0] and 'parts' in result['candidates'][0]['content']:
                        summary = result['candidates'][0]['content']['parts'][0]['text']
                        print("✅ Gemini özet başarıyla alındı!")
                        return summary
                    else:
                        print("⚠️ Gemini response yapısı beklenmedik")
                        return f"Beklenmeyen response yapısı: {result}"
                else:
                    print("⚠️ Gemini candidates bulunamadı")
                    return f"Candidates bulunamadı: {result}"
            else:
                print(f"❌ Gemini API Error: {response.text}")
                return f"Gemini API Hatası ({response.status_code}): {response.text}"
                
        except Exception as e:
            print(f"❌ Gemini API İstek Hatası: {e}")
            return f"Gemini API Hatası: {str(e)}"

def test_gemini_api():
    """Gemini API'yi test et"""
    if GEMINI_API_KEY == "your-gemini-api-key-here":
        return False, "Gemini API key henüz ayarlanmamış"
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    test_data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": "Merhaba, test mesajı"
                    }
                ]
            }
        ],
        "generationConfig": {
            "maxOutputTokens": 10
        }
    }
    
    try:
        response = requests.post(url, json=test_data, timeout=10)
        
        if response.status_code == 200:
            return True, "Gemini API key geçerli ✅"
        else:
            return False, f"Gemini API key hatası: {response.status_code} - {response.text}"
            
    except Exception as e:
        return False, f"API test hatası: {e}"

if __name__ == '__main__':
    print("🔐 Gemini API Key kontrol ediliyor...")
    api_valid, api_message = test_gemini_api()
    
    if not api_valid:
        print(f"❌ {api_message}")
        print("📝 Lütfen dosyanın başındaki GEMINI_API_KEY değişkenini düzenleyin")
        print("🔑 API key almak için: https://makersuite.google.com/app/apikey")
        print("=" * 60)
    else:
        print(f"✅ {api_message}")
    
    print("\n🤖 Gemini YouTube Özetleyici")
    print("📍 http://localhost:8000")
    print("🛑 Durdurmak için Ctrl+C")
    print("=" * 50)
    print("🆓 Gemini Avantajları:")
    print("   • Tamamen ücretsiz!")
    print("   • Günlük 15 request/dakika limit")
    print("   • Güçlü AI modeli")
    print("   • Türkçe desteği mükemmel")
    print("=" * 50)
    
    server = HTTPServer(('localhost', 8000), GeminiHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Durduruldu!")
        server.shutdown()