document.addEventListener('DOMContentLoaded', function() {
    // 标签点击事件
    const tagButtons = document.querySelectorAll('.tag-btn');
    const textarea = document.getElementById('answer');
    
    tagButtons.forEach(button => {
        button.addEventListener('click', function() {
            const tagText = this.getAttribute('data-tag');
            textarea.value = tagText;
            textarea.focus();
            
            // 添加视觉反馈
            tagButtons.forEach(btn => btn.classList.remove('btn-primary', 'active'));
            this.classList.add('btn-primary', 'active');
            this.classList.remove('btn-outline-primary');
        });
    });
    
    // 输入框获得焦点时重置所有标签样式
    textarea.addEventListener('focus', function() {
        tagButtons.forEach(btn => {
            btn.classList.remove('btn-primary', 'active');
            btn.classList.add('btn-outline-primary');
        });
    });
});