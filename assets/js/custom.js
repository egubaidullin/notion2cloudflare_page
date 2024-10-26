function copyToClipboard(button) {
      var codeBlock = button.parentElement.querySelector('code');
    var textToCopy = codeBlock.innerText;
  
      var tempInput = document.createElement('textarea');
    tempInput.value = textToCopy;
    document.body.appendChild(tempInput);
  
      tempInput.select();
    document.execCommand('copy');
  
      document.body.removeChild(tempInput);
    
    button.innerHTML = 'Copied!';
    setTimeout(function() {
      button.innerHTML = '';
    }, 2000);
  }