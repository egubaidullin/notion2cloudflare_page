function copyToClipboard(button) {
    // Найдите ближайший блок кода
    var codeBlock = button.parentElement.querySelector('code');
    var textToCopy = codeBlock.innerText;
  
    // Создайте временный элемент для копирования текста
    var tempInput = document.createElement('textarea');
    tempInput.value = textToCopy;
    document.body.appendChild(tempInput);
  
    // Скопируйте текст в буфер обмена
    tempInput.select();
    document.execCommand('copy');
  
    // Удалите временный элемент
    document.body.removeChild(tempInput);
  
    // Покажите уведомление о копировании
    button.innerHTML = 'Copied!';
    setTimeout(function() {
      button.innerHTML = '';
    }, 2000);
  }