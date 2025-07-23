import streamlit as st
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from qrcode.image.styles.colormasks import SolidFillColorMask
from PIL import Image, ImageDraw
import io
import zipfile

st.set_page_config(page_title="QR 코드 생성기", layout="centered")
st.title("🌀 커스터마이징 QR 코드 생성기 (테두리 포함)")
st.markdown("QR 색상: **검정색**, 스타일: **원형**, 테두리 색상과 두께는 아래에서 설정하세요")

# URL 입력
urls_input = st.text_area("🔗 QR코드를 만들 URL 목록 (한 줄에 하나씩)", height=150)

# 테두리 색상 선택 (컬러 피커)
border_color = st.color_picker("🎨 테두리 색상 선택", "#FF5000")

# 테두리 두께 슬라이더
border_thickness = st.slider("📏 테두리 두께 조절 (픽셀)", min_value=0, max_value=30, value=10)

# 생성 버튼
generate_btn = st.button("🚀 QR 코드 생성")

# QR 생성 함수
def generate_qr_with_border(url, border_rgb, thickness):
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H)
    qr.add_data(url)
    qr.make()
    
    qr_img = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=RoundedModuleDrawer(),
        color_mask=SolidFillColorMask(front_color=(0, 0, 0), back_color=(255, 255, 255))
    ).convert("RGBA")
    
    # 테두리 추가
    bordered_img = Image.new("RGBA", 
                             (qr_img.size[0] + thickness*2, qr_img.size[1] + thickness*2), 
                             (255, 255, 255, 0))  # 투명 배경

    draw = ImageDraw.Draw(bordered_img)
    draw.rectangle(
        [(0, 0), bordered_img.size],
        fill=(255, 255, 255, 255),
        outline=border_rgb,
        width=thickness
    )
    bordered_img.paste(qr_img, (thickness, thickness), qr_img)

    return bordered_img

if generate_btn and urls_input:
    urls = [u.strip() for u in urls_input.strip().split("\n") if u.strip()]
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w") as zf:
        for idx, url in enumerate(urls, start=1):
            border_rgb = tuple(int(border_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
            qr_img = generate_qr_with_border(url, border_rgb, border_thickness)

            st.image(qr_img, caption=f"QR #{idx}", use_column_width=False)
            st.markdown(f"🔗 {url}")

            img_bytes = io.BytesIO()
            qr_img.save(img_bytes, format="PNG")
            zf.writestr(f"qr_{idx}.png", img_bytes.getvalue())

    st.download_button(
        label="📦 모든 QR코드 ZIP으로 다운로드",
        data=zip_buffer.getvalue(),
        file_name="qr_codes_with_border.zip",
        mime="application/zip"
    )
