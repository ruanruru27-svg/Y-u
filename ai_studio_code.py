import streamlit as st
from google import genai
from google.genai import types

# Cấu hình giao diện Web
st.set_page_config(page_title="AI Story Chat", page_icon="📖", layout="wide")
st.title("📖 AI Chat Sáng Tác Truyện")

# Nhập API Key ở thanh bên
with st.sidebar:
    st.header("⚙️ Cài đặt")
    api_key = st.secrets.get("GEMINI_API_KEY") or st.text_input("Nhập Gemini API Key:", type="password")
    
    system_instruction = st.text_area(
        "Thiết lập nhân vật / Bối cảnh truyện:", 
        value="Bạn là một trợ lý sáng tác truyện chuyên nghiệp. Hãy cùng người dùng phát triển cốt truyện một cách lôi cuốn, văn phong giàu hình ảnh và giữ đúng tính cách nhân vật.",
        height=150
    )
    
    if st.button("🔄 Bắt đầu câu chuyện mới", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

if api_key:
    client = genai.Client(api_key=api_key)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Nhập lời thoại hoặc tình tiết tiếp theo..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        formatted_contents = [
            types.Content(
                role="user" if msg["role"] == "user" else "model",
                parts=[types.Part.from_text(text=msg["content"])]
            )
            for msg in st.session_state.messages
        ]

        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            full_response = ""

            try:
                response = client.models.generate_content_stream(
                    model='gemini-2.5-flash',
                    contents=formatted_contents,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.8
                    )
                )

                for chunk in response:
                    if chunk.text:
                        full_response += chunk.text
                        response_placeholder.markdown(full_response + "▌")

                response_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})

            except Exception as e:
                st.error(f"Đã xảy ra lỗi: {e}")
else:
    st.info("👉 Vui lòng nhập Gemini API Key ở thanh bên trái để bắt đầu sáng tác.")