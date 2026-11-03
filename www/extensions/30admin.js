///admin.cgi/status node & search node replace link.
//license: http://www.kmonos.net/nysl/ or public domain. (dual license).

shingetsu.addInitializer(() => {
    function nodelink() {
        const uls = document.querySelectorAll('ul');
        uls.forEach((ul) => {
            const lis = ul.querySelectorAll('li');
            lis.forEach((li) => {
                const node = li.innerHTML;
                const a = document.createElement('a');
                a.href = 'http://' + node.replace('/server.cgi', '/');
                a.innerHTML = node;

                li.innerHTML = '';
                li.appendChild(a);
            });
        });
    }

    if (location.pathname === '/admin.cgi/status') {
        nodelink();
    }
});
