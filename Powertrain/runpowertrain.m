%-----------------------------------------------------------------------
%Copyright (c) 2011,  Ashish Tiwari.
%Developed with the sponsorship of the Defense Advanced Research Projects Agency (DARPA).
% 
%Permission is hereby granted, free of charge, to any person obtaining a copy of this data, including
%any software or models in source or binary form, as well as any drawings, specifications, and
%documentation (collectively "the Data"), to deal in the Data without restriction, including without
%limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
%of the Data, and to permit persons to whom the Data is furnished to do so, subject to the following
%conditions:
%
%The above copyright notice and this permission notice shall be included in all copies or substantial
%portions of the Data.
%
%THE DATA IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
%LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
%NO EVENT SHALL THE AUTHORS, SPONSORS, DEVELOPERS, CONTRIBUTORS, OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
%CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
%OUT OF OR IN CONNECTION WITH THE DATA OR THE USE OR OTHER DEALINGS IN THE DATA.
%-----------------------------------------------------------------------

%-----------------------------------------------------------------------
% This is a MATLAB file to "run" the model in file "powertrain.m"
% Typing runpowertrain on a MATLAB prompt will perform the simulation
% and generate plots.
% There are 2 inputs variables to set before simulating:
% grade: the grade of the road, in the range [0,0.2]
% tps: the throttle position, in the range [0,1]
% See below.
% Sample generated plots are included in the figures/ subdirectory.
%-----------------------------------------------------------------------

clear

tps = 70;
grade = 0.1745;
%tps = 80;
%grade = 0.2;

N = 6;

Tfinal = 30;
T0 = 0;
step = 0.001;

t = [T0: step: Tfinal]';
x0 = zeros(N,1);
j = 1
x = zeros((Tfinal-T0)/step + 1, N);
x(j,:) = x0;
u = zeros((Tfinal-T0)/step + 1, 2);
u(j,1) = 1;
u(j,2) = 1;

for i = T0+step: step: Tfinal
    j = j+1;
    [dots,v,reset] = powertrain(x(j-1,:)',  u(j-1,:)', i);
    if any(reset)
        x(j,:) = reset';
    else
        x(j,:) = x(j-1,:) + step * dots';
    end
    u(j,:) = v';
end
plot(t,x(:,1))  % plot Ts
% plot(t,x(:,2))  % plot vehicle_speed
% plot(t,u(:,2))  % plot gear of vehicle

