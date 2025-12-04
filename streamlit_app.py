# ... existing code ...
    st.markdown(f"""
    <div class="santa-comment-box">
        <strong>🎅 Santa Says:</strong><br><br>
        <em>{data.get("santa_comment", "Ho ho ho!")}</em>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # 4. Action Buttons
    # Use columns to center the buttons
    col_left, col_center, col_right = st.columns([1, 4, 1])

    with col_center:
        if st.button("DOWNLOAD YOUR CERTIFICATE", use_container_width=True):
             st.toast("🖨️ Printing at North Pole HQ...", icon="🎄")
             st.balloons()
             
        if st.button("POST YOUR ROAST", use_container_width=True):
            share_text = f"{verdict_title}\n\nScore: {score}/10\n\n{data.get('roast_content', '')[:100]}..."
            st.info("📋 Ready to share! (Copy the text above)")
            st.code(share_text)
        
        if st.button("START OVER", use_container_width=True):
            st.session_state.result = None
            st.session_state.images = None
            st.session_state.rotation_angles = {}
            st.session_state.show_camera = False
            st.rerun()
