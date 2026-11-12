@echo off
chcp 65001 >nul
setlocal
set S=%~dp0..
set OUT=%S%\output
if not exist "%OUT%" mkdir "%OUT%"

echo [1/2] single panel + linear fit ...
python "%S%\scripts\plot.py" --csv "%S%\examples\demo_spring.csv" --x 0 --y 1 --mode fit ^
  --panel-title "(a) spring: extension vs mass" --out "%OUT%\coordinate_plot_demo1.png"

echo [2/2] two panels (fit + smooth) ...
python "%S%\scripts\plot.py" --csv "%S%\examples\demo_spring.csv" --x 0 --y 1 --mode fit ^
  --panel-title "(a) spring: extension vs mass" ^
  --panel2-csv "%S%\examples\demo_rtd.csv" --panel2-x 0 --panel2-y 1 --panel2-mode smooth ^
  --panel2-title "(b) thermistor: R vs T" ^
  --out "%OUT%\coordinate_plot_demo2.png"

echo done. output dir: %OUT%
pause
