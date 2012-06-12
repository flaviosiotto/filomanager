from distutils.core import setup

if __name__ == '__main__':

	if not os.path.exists('~/.filomanager/log'):
		os.makedirs('~/.filomanager/log')

	if not os.path.exists('~/.filomanager/templates'):
		os.makedirs('~/.filomanager/templates')

	if not os.path.exists('~/.filomanager/Menuchef'):
		os.makedirs('~/.filomanager/Menuchef')

	setup(
		author='Flavio Siotto',
		author_email='flavio.siotto@gmail.com',
		name='FiloManager',
		version='0.4',
		packages=['filomanager','filomanager.jobs', 'filomanager.stages', 'filomanager.ui'],
		package_data={	'filomanager.ui':['glade/*.glade','images/*.png']},
		data_files=[('etc', ['FiloManager.conf']),
					('usr/share/applications/', ['data/filomanager.desktop']),
					('usr/share/icons/hicolor/scalable/apps', ['data/filomanager.svg']),
					('~/.filomanager/templates', ['data/templates/menu-chef.ott'])
					],
		long_description=open('README').read(),
		scripts=['bin/filomanager']
	)
