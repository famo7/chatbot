(async function() {
    // Get the script URL to determine the host
    const scripts = document.getElementsByTagName('script');
    const currentScript = scripts[scripts.length - 1];
    const scriptSrc = currentScript.src;
    const host = new URL(scriptSrc).origin;

    // Fetch company config for colors
    let primaryColor = '#2563eb';
    let companyName = 'Chat';
    try {
        const response = await fetch(`${host}/config`);
        const config = await response.json();
        primaryColor = config.colors?.primary || '#2563eb';
        companyName = config.company_name || 'Chat';
    } catch (e) {
        console.log('Could not load config, using defaults');
    }

    // Create wrapper div
    const wrapper = document.createElement('div');
    wrapper.id = 'chatbot-widget-wrapper';
    wrapper.style.cssText = 'position:fixed;bottom:20px;right:20px;z-index:2147483647;font-family:system-ui,-apple-system,sans-serif;';

    // Create toggle button
    const toggleBtn = document.createElement('button');
    toggleBtn.id = 'chatbot-toggle';
    toggleBtn.innerHTML = '💬';
    toggleBtn.style.cssText = `
        width:60px;
        height:60px;
        border-radius:50%;
        background:${primaryColor};
        border:none;
        cursor:pointer;
        font-size:24px;
        color:white;
        box-shadow:0 4px 20px rgba(0,0,0,0.18);
        transition:transform 0.2s ease, background 0.2s ease;
        display:flex;
        align-items:center;
        justify-content:center;
    `;
    toggleBtn.onmouseover = () => {
        toggleBtn.style.transform = 'scale(1.08)';
        toggleBtn.style.filter = 'brightness(1.1)';
    };
    toggleBtn.onmouseout = () => {
        toggleBtn.style.transform = 'scale(1)';
        toggleBtn.style.filter = 'brightness(1)';
    };
    toggleBtn.title = companyName;

    // Create iframe container
    const iframeContainer = document.createElement('div');
    iframeContainer.id = 'chatbot-iframe-container';
    iframeContainer.style.cssText = `
        position:fixed;
        bottom:90px;
        right:20px;
        width:380px;
        height:560px;
        border-radius:20px;
        overflow:hidden;
        box-shadow:0 8px 40px rgba(0,0,0,0.14);
        opacity:0;
        transform:translateY(16px) scale(0.97);
        pointer-events:none;
        transition:opacity 0.25s ease, transform 0.25s ease;
        background:#fff;
        z-index:2147483647;
    `;

    // Create iframe
    const iframe = document.createElement('iframe');
    iframe.src = host;
    iframe.style.cssText = 'width:100%;height:100%;border:none;';
    iframe.title = companyName;

    // Toggle functionality
    let isOpen = false;
    toggleBtn.onclick = function() {
        isOpen = !isOpen;
        if (isOpen) {
            iframeContainer.style.opacity = '1';
            iframeContainer.style.transform = 'translateY(0) scale(1)';
            iframeContainer.style.pointerEvents = 'all';
            toggleBtn.innerHTML = '✕';
        } else {
            iframeContainer.style.opacity = '0';
            iframeContainer.style.transform = 'translateY(16px) scale(0.97)';
            iframeContainer.style.pointerEvents = 'none';
            toggleBtn.innerHTML = '💬';
        }
    };

    // Mobile responsive
    if (window.innerWidth <= 480) {
        iframeContainer.style.width = 'calc(100vw - 40px)';
        iframeContainer.style.height = '70vh';
        iframeContainer.style.right = '20px';
    }

    // Assemble
    iframeContainer.appendChild(iframe);
    wrapper.appendChild(iframeContainer);
    wrapper.appendChild(toggleBtn);
    document.body.appendChild(wrapper);
})();
