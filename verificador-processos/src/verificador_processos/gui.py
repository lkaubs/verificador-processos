import eel

# Set web files folder and optionally specify which file types to check for eel.expose()
#   *Default allowed_extensions are: ['.js', '.html', '.txt', '.htm', '.xhtml']
eel.init('/home/lkabus/Documentos/python/verificador-processos/verificador-processos/src/verificador_processos/web', allowed_extensions=['.js', '.html'])

@eel.expose                         # Expose this function to Javascript
def say_hello_py(x):
    print('Hello from %s' % x)
say_hello_py('Python World!')

eel.start('hello.html', shutdown_delay=0.1)             # Start (this blocks and enters loop)
