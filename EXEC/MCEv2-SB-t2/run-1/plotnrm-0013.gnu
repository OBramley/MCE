set terminal png
set output "Norm-0013.png"
set title "Graph of Norm"
set xlabel "Time (au)"
set ylabel "Norm"
plot "normpop-0013.out" u 1:2 t "Norm" w l