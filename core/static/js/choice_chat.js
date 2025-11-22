document.addEventListener('DOMContentLoaded', function() {
    // 为选项添加交互效果
    const optionLabels = document.querySelectorAll('.option-label');
    
    optionLabels.forEach(label => {
        label.addEventListener('click', function() {
            // 移除同组其他选项的active状态
            const questionCard = this.closest('.question-card');
            const allLabelsInGroup = questionCard.querySelectorAll('.option-label');
            allLabelsInGroup.forEach(l => l.classList.remove('active'));
            
            // 添加当前选项的active状态
            this.classList.add('active');
            
            // 确保单选按钮被选中
            const radioInput = this.previousElementSibling;
            if (radioInput && radioInput.type === 'radio') {
                radioInput.checked = true;
            }
        });
    });
    
    // 初始化时检查已选中的选项
    optionLabels.forEach(label => {
        const radioInput = label.previousElementSibling;
        if (radioInput && radioInput.checked) {
            label.classList.add('active');
        }
    });
});
