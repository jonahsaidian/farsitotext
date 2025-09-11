from PyInstaller.utils.hooks import copy_metadata

datas = []
try:
	datas += copy_metadata('streamlit')
except Exception:
	pass

