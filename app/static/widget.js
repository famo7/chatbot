(async function() {
    const scripts = document.getElementsByTagName('script');
    const currentScript = scripts[scripts.length - 1];
    const host = new URL(currentScript.src).origin;

    // Fetch company config
    let primaryColor = '#2563eb';
    let companyName = 'Chat';
    try {
        const res = await fetch(`${host}/config`);
        const config = await res.json();
        primaryColor = config.colors?.primary || '#2563eb';
        companyName = config.company_name || 'Chat';
    } catch (e) {}

    // ── Toggle button ──
    const toggleBtn = document.createElement('button');
    toggleBtn.innerHTML = '💬';
    toggleBtn.style.cssText = `
        position: fixed;
        bottom: 24px;
        right: 24px;
        z-index: 2147483647;
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background: ${primaryColor};
        border: none;
        cursor: pointer;
        font-size: 24px;
        color: white;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
        transition: transform 0.2s ease, filter 0.2s ease;
        display: flex;
        align-items: center;
        justify-content: center;
    `;
    toggleBtn.onmouseover = () => toggleBtn.style.transform = 'scale(1.08)';
    toggleBtn.onmouseout = () => toggleBtn.style.transform = 'scale(1)';

    // ── Chat iframe ──
    const chatBox = document.createElement('div');
    chatBox.style.cssText = `
        position: fixed;
        bottom: 100px;
        right: 24px;
        z-index: 2147483646;
        width: 380px;
        height: 560px;
        border-radius: 20px;
        overflow: hidden;
        box-shadow: 0 8px 40px rgba(0,0,0,0.15);
        opacity: 0;
        transform: translateY(16px) scale(0.97);
        pointer-events: none;
        transition: opacity 0.25s ease, transform 0.25s ease;
        background: #fff;
    `;

    const iframe = document.createElement('iframe');
    iframe.src = `${host}/embed`;
    iframe.style.cssText = 'width:100%;height:100%;border:none;display:block;';
    iframe.title = companyName;
    chatBox.appendChild(iframe);

    // Mobile
    if (window.innerWidth <= 480) {
        chatBox.style.width = 'calc(100vw - 32px)';
        chatBox.style.height = '70vh';
        chatBox.style.right = '16px';
        chatBox.style.bottom = '90px';
        toggleBtn.style.right = '16px';
        toggleBtn.style.bottom = '16px';
    }

    // ── Toggle logic ──
    let isOpen = false;
    toggleBtn.onclick = () => {
        isOpen = !isOpen;
        if (isOpen) {
            chatBox.style.opacity = '1';
            chatBox.style.transform = 'translateY(0) scale(1)';
            chatBox.style.pointerEvents = 'all';
            toggleBtn.innerHTML = '✕';
        } else {
            chatBox.style.opacity = '0';
            chatBox.style.transform = 'translateY(16px) scale(0.97)';
            chatBox.style.pointerEvents = 'none';
            toggleBtn.innerHTML = '💬';
        }
    };

    document.body.appendChild(chatBox);
    document.body.appendChild(toggleBtn);
})();
