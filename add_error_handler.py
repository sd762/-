import re

with open("index.html", "r", encoding="utf-8") as f:
    content = f.read()

error_handler = """
    <script>
        window.onerror = function(msg, url, lineNo, columnNo, error) {
            const errDiv = document.createElement('div');
            errDiv.style.position = 'fixed';
            errDiv.style.top = '0';
            errDiv.style.left = '0';
            errDiv.style.width = '100%';
            errDiv.style.background = 'red';
            errDiv.style.color = 'white';
            errDiv.style.zIndex = '999999';
            errDiv.style.padding = '20px';
            errDiv.innerHTML = '<h3>Global Error:</h3><p>' + msg + '</p><p>' + (error && error.stack ? error.stack : '') + '</p>';
            document.body.appendChild(errDiv);
            return false;
        };
        window.onunhandledrejection = function(event) {
            const errDiv = document.createElement('div');
            errDiv.style.position = 'fixed';
            errDiv.style.top = '0';
            errDiv.style.left = '0';
            errDiv.style.width = '100%';
            errDiv.style.background = 'orange';
            errDiv.style.color = 'white';
            errDiv.style.zIndex = '999998';
            errDiv.style.padding = '20px';
            errDiv.innerHTML = '<h3>Promise Error:</h3><p>' + (event.reason ? (event.reason.message || event.reason) : 'Unknown') + '</p>';
            document.body.appendChild(errDiv);
        };
    </script>
"""

content = content.replace("</head>", error_handler + "</head>")

with open("index.html", "w", encoding="utf-8") as f:
    f.write(content)
