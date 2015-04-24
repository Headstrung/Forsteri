clear all;
close all;
clc;

function fun(x, Xtr, Xti)
    n = [0 : size(Xtr)(2) - 1];
    fun = sum(Xtr .* cos(x * n) + Xti .* sin(x * n));
end

X = [1, 2, 3, 1, 2, 1, 3];
Xt = fft(X);
Xtr = real(Xt);
Xti = imag(Xt);

val = zeros(1, 7);

for i = 1 : 7
    val(i) = fun(X(i), Xtr, Xti);
end
