document.addEventListener('DOMContentLoaded', function() {
    // 配置marked选项
    marked.setOptions({
        breaks: true,
        gfm: true,
        highlight: function(code, lang) {
            // 简单的代码高亮
            return '<pre class="bg-dark text-light p-2 rounded"><code>' + 
                   code.replace(/</g, '&lt;').replace(/>/g, '&gt;') + 
                   '</code></pre>';
        }
    });
    
    // 渲染所有Markdown内容
    function renderMarkdown() {
        // 学习内容
        const contentElement = document.getElementById('content-markdown');
        if (contentElement) {
            const cleanContent = DOMPurify.sanitize(marked.parse(contentElement.textContent));
            contentElement.innerHTML = cleanContent;
        }
        
        // 习题内容
        const exerciseElement = document.getElementById('exercise-markdown');
        if (exerciseElement) {
            const cleanExercise = DOMPurify.sanitize(marked.parse(exerciseElement.textContent));
            exerciseElement.innerHTML = cleanExercise;
        }
        
        // 答案内容
        const answerElement = document.getElementById('answer-markdown');
        if (answerElement) {
            const cleanAnswer = DOMPurify.sanitize(marked.parse(answerElement.textContent));
            answerElement.innerHTML = cleanAnswer;
        }
        
        // 答疑回答
        document.querySelectorAll('[id^="qa-answer-"]').forEach(element => {
            const cleanQA = DOMPurify.sanitize(marked.parse(element.textContent));
            element.innerHTML = cleanQA;
        });
    }
    
    renderMarkdown();
    
    // 习题答案显示/隐藏功能
    const toggleAnswerButtons = document.querySelectorAll('.toggle-answer');
    
    toggleAnswerButtons.forEach(button => {
        button.addEventListener('click', function() {
            const answerSection = this.closest('.card-body').querySelector('.answer-section');
            const isVisible = answerSection.style.display !== 'none';
            
            if (isVisible) {
                answerSection.style.display = 'none';
                this.innerHTML = '<i class="fas fa-eye me-1"></i>显示答案';
                this.classList.remove('btn-primary');
                this.classList.add('btn-outline-primary');
            } else {
                answerSection.style.display = 'block';
                this.innerHTML = '<i class="fas fa-eye-slash me-1"></i>隐藏答案';
                this.classList.remove('btn-outline-primary');
                this.classList.add('btn-primary');
            }
        });
    });
    
    // 页面加载时滚动到锚点
    const hash = window.location.hash;
    if (hash) {
        const targetElement = document.querySelector(hash);
        if (targetElement) {
            setTimeout(() => {
                targetElement.scrollIntoView({ behavior: 'smooth' });
            }, 100);
        }
    }
    
    // 模块链接点击处理
    document.querySelectorAll('.module-link').forEach(link => {
        link.addEventListener('click', function(e) {
            if (this.classList.contains('text-muted')) {
                e.preventDefault();
                alert('当前学习内容还未生成，请按顺序学习或点击下一课继续');
            }
        });
    });
});