add_py_modules(
	__init__.py
	blendomatic.py
	colortable.py
	drs.py
	langcodes.py
	pefile.py
	peresource.py
)

add_cython_modules(
	sld.pyx
	slp.pyx
	smp.pyx
	smx.pyx
)

add_pxds(
	__init__.pxd
)

add_subdirectory(datfile)
add_subdirectory(hardcoded)
