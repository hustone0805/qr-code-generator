# 파일명 예시: qr_generator_app.py

import streamlit as st
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from qrcode.image.styles.colormasks import SolidFillColorMask
from PIL import Image
import io
import zipfile

st.set_page_config(page_title="QR 코드 생성기", layout="centered")

st.title("🎨 커스터마이징 QR 코드 생성기")
st.markdown("QR 색상: **검정색**, 테두리: **RGB(255, 80, 0)**, 스타일: **원형**, 로고 삽입")

# 입력 받기
urls_input = st.text_area("🔗 QR코드를 만들 URL 목록 (한 줄에 하나씩 입력하세요)", height=150)
uploaded_logo = st.file_uploader("🖼 로고 이미지 업로드 (PNG 권장)", type=["png", "jpg", "jpeg"])

generate_btn = st.button("🚀 QR 코드 생성하기")

def generate_qr(url, logo_img=None):
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H)
    qr.add_data(url)
    qr.make()
    
    img = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=RoundedModuleDrawer(),
        color_mask=SolidFillColorMask(front_color=(0, 0, 0), back_color=(255, 255, 255))  # 검정/흰색
    ).convert("RGBA")

    if logo_img:
        logo_img = logo_img.resize((60, 60))
        pos = ((img.size[0] - logo_img.size[0]) // 2, (img.size[1] - logo_img.size[1]) // 2)
        img.paste(logo_img, pos, logo_img)

    return img

if generate_btn and urls_input:
    urls = [u.strip() for u in urls_input.strip().split("\n") if u.strip()]
    results = []
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, "w") as zf:
        for idx, url in enumerate(urls, start=1):
            logo = Image.open(uploaded_logo).convert("RGBA") if uploaded_logo else None
            qr_img = generate_qr(url, logo)
            
            # 화면 출력
            st.image(qr_img, caption=f"QR #{idx}", use_column_width=False)
            st.markdown(f"🔗 {url}")

            # ZIP 저장
            img_bytes = io.BytesIO()
            qr_img.save(img_bytes, format="PNG")
            zf.writestr(f"qr_{idx}.png", img_bytes.getvalue())
    
    st.download_button(
        label="📦 모든 QR코드 ZIP으로 다운로드",
        data=zip_buffer.getvalue(),
        file_name="qr_codes.zip",
        mime="application/zip"
    )
