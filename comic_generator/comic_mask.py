import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image

st.title("漫画panel自由分割线编辑器")

st.write("用画笔工具在下方画布上手动画漫画panel分格线，支持自由线条、Z形、斜切等，生成面板mask。")

canvas_result = st_canvas(
    fill_color="rgba(0, 0, 0, 0)",  # 无填充，仅画线
    stroke_width=6,
    stroke_color="#000000",
    background_color="#ffffff",
    width=st.sidebar.slider("画布宽度(px)", 512, 2048, 1024, step=64),
    height=st.sidebar.slider("画布高度(px)", 512, 3072, 1536, step=64),
    drawing_mode=st.sidebar.selectbox(
        "工具选择",
        ("freedraw", "line", "rect", "circle", "transform"),
        index=1
    ),  # 建议默认"line"用于panel分格，"freedraw"用于随手画
    key="canvas",
    update_streamlit=True,
)

if canvas_result.image_data is not None:
    mask_img = Image.fromarray(canvas_result.image_data.astype("uint8"))
    st.image(mask_img, caption="你的自定义分格mask预览", use_column_width=True)
    st.download_button("下载分格mask为PNG", mask_img.tobytes(), file_name="custom_panel_mask.png", mime="image/png")
    st.success("可以把这个分格mask用于下游AIGC漫画管线。")

st.info("Tip：推荐选择 'line' 工具画直线, 'freedraw' 可画随手曲线。画好后可直接下载mask图。")