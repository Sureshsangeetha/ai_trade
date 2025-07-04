function showTab(tabId) {
    // Hide all tab contents
    document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
    // Remove active class from all buttons
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    // Show selected tab
    document.getElementById(tabId).classList.add('active');
    // Set active class on the clicked button
    const btns = document.querySelectorAll('.tab-btn');
    if(tabId === 'dashboard') btns[0].classList.add('active');
    if(tabId === 'backtest') btns[1].classList.add('active');
    if(tabId === 'news') btns[2].classList.add('active');
    if(tabId === 'heatmap') btns[3].classList.add('active');
    if(tabId === 'portfolio') btns[4].classList.add('active');
}

// Show dashboard tab by default on load
window.onload = function() {
    showTab('dashboard');
};
