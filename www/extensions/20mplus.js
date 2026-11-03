// Inconsolata, M PLUS 2 and M PLUS Rounded 1c font patch.
// from a shinGETsu user.
// converted to shinGETsu extension.

shingetsu.initialize(function () {
  const links = [
    { rel: 'preconnect', href: 'https://fonts.googleapis.com' },
    { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: true },
    { 
      rel: 'stylesheet', 
      href: 'https://fonts.googleapis.com/css2?family=Inconsolata:wght@200..900&family=M+PLUS+2:wght@100..900&family=M+PLUS+Rounded+1c&display=swap' 
    }
  ];

  links.forEach(attr => {
    const link = document.createElement('link');
    for (const key in attr) {
      if (key === 'crossorigin') {
        link.crossOrigin = '';
      } else {
        link.setAttribute(key, attr[key]);
      }
    }
    document.head.appendChild(link);
  });
});
