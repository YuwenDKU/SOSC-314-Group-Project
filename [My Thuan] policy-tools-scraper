import requests
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader

# Define instruments
instruments = {
    'Subsidies': ['补贴', '补助', '奖励'],
    'Tax Reductions': ['税收', '减免', '免税', '退税'],
    'Land': ['土地', '出让', '用地'],
    'Funds': ['引导基金', '股权', "基金"],
    'Credit': ['信贷', '贷款', '担保'],
}
# Function for HTML URLs (Shanghai, Suzhou)
def get_text_from_html(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup.get_text(separator=' ', strip=True)

# Function for local PDFs (Ningbo, Nanjing, Hangzhou)
def get_text_from_pdf(filename):
    pdf_reader = PdfReader(filename)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text

# Function for keywords checking
def check_keywords(text):
    for category, keywords in instruments.items():
        found = [kw for kw in keywords if kw in text]
        if found:
            print(f"✅ {category}: {', '.join(found)}")
        else:
            print(f"❌ {category}: Not found")
            
# SHANGHAI (HTML)
print("SHANGHAI")
shanghai_text = get_text_from_html('https://www.shanghai.gov.cn/nw12338/20260515/a97f758537314ce7b2c0e26614e179f6.html')
check_keywords(shanghai_text)

# SUZHOU (HTML)
print("SUZHOU")
suzhou_text = get_text_from_html('https://www.suzhou.gov.cn/szsrmzf/czyjsbg/202603/57f2227cdfff4bef8a8c37ee8580add5.shtml')
check_keywords(suzhou_text)

# NINGBO (Local PDF)
print("NINGBO")
ningbo_text = get_text_from_pdf('ningbo.cn.pdf')
check_keywords(ningbo_text)

# NANJING (Local PDF)
print("NANJING")
nanjing_text = get_text_from_pdf('nanjing.gov.cn.pdf')
check_keywords(nanjing_text)

# HANGZHOU (Local PDF)
print("HANGZHOU")
hangzhou_text = get_text_from_pdf('hangzhou.gov.cn.pdf')
check_keywords(hangzhou_text)
