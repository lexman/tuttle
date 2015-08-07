set terminal png
set output "characters_count.png"
plot "characters_count.dat" using 2: xtic(1) with histogram linecolor "green"
