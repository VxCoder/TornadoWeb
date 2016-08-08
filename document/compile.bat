@echo off

sphinx-apidoc -F -o ./ ../controllers -H TornadoWeb -A WSB

call make epub

pause
