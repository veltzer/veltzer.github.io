<html>
	<head>
		<link rel="icon" href="/favicon.svg" type="image/svg+xml">
		<link rel="apple-touch-icon" href="/favicon.svg">
	</head>
	<body>
		Welcome to Mark Veltzer's website on github using github pages.
		<h2>My calendar integration I'm working on</h2>
		<%
			prefix="\t\t"
			context.write(f"<ul>\n")
			import os
			current_dir = "templates/docs"
			for f in sorted(os.listdir(current_dir)):
				if os.path.isfile(os.path.join(current_dir, f)) and not f.startswith("."):
					no_mako = f.rsplit('.', 1)[0]
					base = f.split('.')[0]
					context.write(f"{prefix}\t<li><a href=\"{no_mako}\">{base}</a></li>\n")
			context.write(f"{prefix}</ul>")
		%>
	</body>
</html>
