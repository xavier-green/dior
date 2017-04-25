from flask import Flask

import flask_admin as admin

class Logs(admin.BaseView):
	@admin.expose('/')
	def index(self):
		with open("logs.txt") as f:
			content = f.readlines()
			content = [x for x in content]
			print(content)
			# center = ""
			data = []
			for entry in content:
				# center += "<tr>"
				words = entry.split("||")
				data.append(words)
				# for word in words:
				# 	center += "<td style='border: 1px solid #dddddd;'>"+word+"</td>"
				# center += "</tr>"

		return self.render('logs.html', data=data)


# Create flask app
app = Flask(__name__, template_folder='templates')
app.debug = True

# Flask views
@app.route('/')
def index():
	return '<a href="/admin/">This is nothing but a blank page. Click here to go to something more interesting.</a>'

# Create admin navbar
admin = admin.Admin(name="Dior Admin Page", template_mode='bootstrap3')
admin.add_view(Logs(name="Logs"))
admin.init_app(app)

if __name__ == '__main__':

	# Start app
	app.run()
