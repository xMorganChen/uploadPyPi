import streamlit as st
import os
import subprocess
import tempfile

st.set_page_config(page_title="PyPI Uploader", page_icon="📦")

st.title("📦 PyPI 自動上傳工具")
st.write("透過這個介面，將你本機 build 好的 `.whl` 檔案直接推送到 PyPI。")

# 1. 檔案上傳區塊 (支援多個檔案)
uploaded_files = st.file_uploader(
    "請選擇你要上傳的 .whl 檔案", 
    type=['whl'], 
    accept_multiple_files=True
)

if uploaded_files:
    st.info(f"✅ 準備上傳 {len(uploaded_files)} 個檔案")

# 2. Token 輸入區塊 (密碼格式，不會顯示明文)
st.markdown("---")
pypi_token = st.text_input(
    "⚠️ 請輸入你的 PyPI API Token", 
    type="password", 
    help="就是 pypi- 開頭的那串，輸入後不會顯示字元是正常的。"
)

# 3. 執行按鈕
if st.button("🚀 開始上傳到 PyPI", type="primary"):
    if not uploaded_files:
        st.warning("請先上傳至少一個 `.whl` 檔案！")
    elif not pypi_token:
        st.warning("請輸入 PyPI Token！")
    else:
        with st.spinner("上傳中，請稍候..."):
            # 建立一個暫時的資料夾來存放上傳的檔案，執行完畢會自動清理
            with tempfile.TemporaryDirectory() as temp_dir:
                file_paths = []
                
                # 將 Streamlit 記憶體中的檔案寫入暫存資料夾
                for uploaded_file in uploaded_files:
                    file_path = os.path.join(temp_dir, uploaded_file.name)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    file_paths.append(file_path)
                
                # 準備環境變數供 twine 使用
                env = os.environ.copy()
                env['TWINE_USERNAME'] = '__token__'
                env['TWINE_PASSWORD'] = pypi_token
                
                # 組合 twine 指令
                cmd = ["twine", "upload"] + file_paths
                
                try:
                    # 使用 subprocess 執行 twine
                    result = subprocess.run(
                        cmd, 
                        env=env, 
                        capture_output=True, 
                        text=True, 
                        check=True
                    )
                    st.success("🎉 上傳成功！")
                    with st.expander("查看詳細輸出紀錄"):
                        st.code(result.stdout)
                        
                except subprocess.CalledProcessError as e:
                    st.error("❌ 上傳失敗！請檢查 Token 是否正確，或版本號是否已存在。")
                    with st.expander("查看錯誤訊息"):
                        st.code(e.stderr)