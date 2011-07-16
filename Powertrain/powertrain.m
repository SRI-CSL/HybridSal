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
% This is a MATLAB simulation model of a powertrain.
% It is inspired from the model created by Aloncrit Chutinan,
% Ken Butts and Bill Milam (Ford Motor Company).
%-----------------------------------------------------------------------

function [sys,v,reset]  = powertrain(x,u,t)

if any(u == 0)
    reset = x; 
    sys = [0 0 0 0 0 0]';
    v = u;
    return
end

% Model parameters
M = 1644.0 + 125.0;	% vehicle mass (kg)
Hf = 0.310;		% static ground-to-axle height of front wheel (m)
Iwf = 2.8;		% front wheel inertia (both sides) (kg-m^2)
Ks = 6742.0;		% driveshaft spring constant (Nm/rad)

Rsi = 0.2955; 		% input sun gear ratio
Rci = 0.6379;		% input carrier gear ratio
Rcr = 0.7045;		% Reaction carrier gear ratio
Rd = 0.3521;		% final drive gear ratio

R1 = Rci*Rsi/(1-Rci*Rcr);	% 1st gear ratio
R2 = Rci;			% 2nd gear ratio

AR2 = 4.125;
c2_mu1 = 0.1316;
c2_mu2 = 0.0001748;

It = 0.05623;		% turbine inertia (kg-m^2)
Isi = 0.001020;		% input sun gear inertia  (kg-m^2)
Ici = 0.009020;		% input carrier gear inertia (kg-m^2)
Icr = 0.005806;		% reaction carrier gear inertia (kg-m^2)

It1 = It + Isi + R1*R1*Icr + R1*R1*Ici/(R2*R2);
It2 = It + Ici + R2*R2*Icr + R2*R2*Isi/(R1*R1);

Icr12 = Icr + Isi/(R1*R1) + Ici/(R2*R2);

c2_table.y = [0 1 1 0];

Pc2max = 400.0;		% kPa
m_s_to_km_h = 3.6;
pc2_torque_phase = 0.4;

% Model inputs
tps = evalin('base', 'tps');
grade = evalin('base', 'grade');

% continuous states
Ts = x(1);
veh_speed = x(2);
pc2_filter = x(3);
wt = x(4);
wcr = x(5);
z = x(6);

% discrete inputs
gear_schedule = u(1);
dynamic_mode = u(2);

% gear schedule state enumeration
FIRST_GEAR = 1;
TRANSITION12_SHIFTING = 2;
SECOND_GEAR = 3;
TRANSITION21_SHIFTING = 4;

% dynamic mode enumeration
FIRST = 1;
TORQUE12 = 2;
SECOND = 4;
INERTIA12 = 3;
INERTIA21 = 5;
TORQUE21 = 6;

% compute variables that depend on cont. state
if ismember(dynamic_mode,[FIRST,TORQUE12,TORQUE21])
    wci = R1/R2 * wt;
    wsi = wt;
elseif ismember(dynamic_mode,[INERTIA12,INERTIA21])
    wci = wcr/R2;
    wsi = wcr/R1;
elseif ismember(dynamic_mode,[SECOND])
    wci = wt;
    wsi = wt*R2/R1;
end

% compute variables that depend on disc. state
if ismember(gear_schedule,[FIRST_GEAR,TRANSITION21_SHIFTING])
    to_gear = 1;
elseif ismember(gear_schedule,[SECOND_GEAR,TRANSITION12_SHIFTING])
    to_gear = 2;
end

% compute other intermediate variables
Tt = 1.7*tps + 30;

pc1max = 1000;
pc1 = pc1max;
pc2_target = Pc2max * c2_table.y(to_gear);
pc2 = pc2_filter + pc2_torque_phase * pc2_target;

% Ashish: Added Tc1 equations here; sgn1 and sgn2 set to 0
% instead of 1 when value less than 0.5
c1mu1 = 0.1316;		% static coeff of friction (dimensionless)
c1mu2 = 0.0001748;	% dynamic coeff of friction (rad^-)
AR1 = 2.912;		% clutch gain (m^3)
c1slip = wt - wsi;
if (c1slip > -0.5) & (c1slip < 0.5)
    c1slip = 0;
    sgn1 = 1;
else
    sgn1 = sign(c1slip);
end
Tc1 = sgn1 * (c1mu2 * abs(c1slip) + c1mu1) * AR1 * pc1;

c2slip = wt - wci;
if (c2slip > -0.5) & (c2slip < 0.5)
    c2slip = 0;
    sgn2 = 1;
else
    sgn2 = sign(c2slip);
end
Tc2 = sgn2 * (c2_mu2 * abs(c2slip) + c2_mu1) * AR2 * pc2;
if (rem(t,1)==0)
    pc2,t,Tc2
end

Ts_dot = Ks * (Rd*wcr - veh_speed/Hf - 0.001 * Ts);
veh_speed_dot = (Ts/Hf - M*9.81*sin(grade)) / (M + 2*Iwf/(Hf*Hf)) ;
pc2_filter_dot = -pc2_filter + (1 - pc2_torque_phase)*pc2_target;

if ismember(dynamic_mode, [FIRST])
    wt_dot = 1/It1 * (Tt - R1*Rd*Ts);
elseif ismember(dynamic_mode, [TORQUE12,TORQUE21])
    wt_dot = 1/It1 * (Tt - R1*Rd*Ts - (1 - R1/R2)*Tc2);
elseif ismember(dynamic_mode, [INERTIA12,INERTIA21])
    wt_dot = 1/It * (Tt - Tc2);
elseif ismember(dynamic_mode, [SECOND])
    wt_dot = 1/It2 * (Tt - R2*Rd*Ts);
end

if ismember(dynamic_mode, [FIRST,TORQUE12,TORQUE21])
    wcr_dot = R1 * wt_dot;
    wci_dot = R1/R2 * wt_dot;
    wsi_dot = wt_dot;
elseif ismember(dynamic_mode, [INERTIA12,INERTIA21])
    wcr_dot = 1/Icr12 * (Tc2/R2 - Rd*Ts);
    wci_dot = wcr_dot/R2;
    wsi_dot = wcr_dot/R1;
elseif ismember(dynamic_mode, [SECOND])
    wcr_dot = R2*wt_dot;
    wci_dot = wt_dot;
    wsi_dot = wt_dot*R2/R1;
end

z_dot = pc2_filter_dot * wt + wt_dot*pc2_filter;

sys = [Ts_dot
    veh_speed_dot
    pc2_filter_dot
    wt_dot
    wcr_dot
    z_dot];

if ismember(dynamic_mode, [FIRST,TORQUE12,TORQUE21])
    wcr_reset = R1*wt;
elseif ismember(dynamic_mode, [INERTIA12,INERTIA21])
    wcr_reset = wcr;
elseif ismember(dynamic_mode, [SECOND])
    wcr_reset = R2*wt;
end

reset = [Ts
    veh_speed
    pc2_filter
    wt
    wcr_reset
    z];

% Ashish
% the dynamic_mode is generated by the transmission state machine
% The state machines, which updates dynamic_mode, is shown below
Isi12 = It1 - It;
Ici12 = It2 - It;
RTsp1 = Isi12 * wsi_dot  + R1*Rd*Ts - R1/R2 * Tc2;
if dynamic_mode == FIRST % gear == 1
    Rtc2up = 0;
    Rtc2down = 0;
else
    Rtc2up = Tt - It * wt_dot;
    Rtc2down = R2*Rd*Ts + Ici12*wci_dot;
end
if (rem(t,1) == 0)
    t,Rtc2up,Rtc2down
end

if (dynamic_mode == FIRST)
    gear = 1;
elseif (dynamic_mode == SECOND)
    gear = 1;
else
    gear = 1.5;
end

old_reset = reset;
reset = [0; 0; 0; 0; 0; 0];
v = zeros(size(u));
if (dynamic_mode == FIRST) & (Tc2 > 1)
    v(2) = TORQUE12;
    gear = 1.5;
    reset = old_reset;
    'changing mode from FIRST to TORQUE12; Tc2 > 1'
    t
    Tc2
elseif (dynamic_mode == TORQUE12) & (RTsp1 <= 0)
    v(2) = INERTIA12;
    gear = 1.5;
    reset = old_reset;
    'changing mode from TORQUE12 to INERTIA12: RTsp1 <= 0?'
    t
    RTsp1
elseif (dynamic_mode == INERTIA12) & (c2slip <= 0) & pc2 > 399
    % & abs(Tc2) > abs(Rtc2up) & abs(Tc2) > abs(Rtc2down)
    v(2) = SECOND;
    gear = 2;
    reset = old_reset;
    'changing mode from INERTIA12 to 2nd: Tc2 > RTc2up, Rtc2down?'
    t
    Tc2
    Rtc2up
    Rtc2down
elseif (dynamic_mode == SECOND) & ~(abs(Tc2) > abs(Rtc2up) & abs(Tc2) > abs(Rtc2down))
    v(2) = INERTIA21;
    gear = 1.5;
    reset = old_reset;
    'changing mode from 2nd to INERTIA21: not Tc2 > RTc2up, Rtc2down?'
    t
    Tc2
    Rtc2up
    Rtc2down
elseif (dynamic_mode == INERTIA21) & (c1slip >= 0 & RTsp1 >= 0)
    v(2) = TORQUE21;
    gear = 1.5;
    reset = old_reset;
    'changing mode from INERTIA21 to TORQUE21: c1slip >=0, RTsp1 >=0?'
    t
    c1slip
    RTsp1
elseif (dynamic_mode == TORQUE21) & (Tc1 > Tt & Tc2 <= 1)
    v(2) = FIRST;
    gear = 1;
    reset = old_reset;
    'changing mode from TORQUE21 to FIRST'
    t
else
    v(2) = u(2);
end

if (dynamic_mode == INERTIA12) & (rem(t,1) == 0)
    c2slip 
    Tc2 
    Rtc2up 
    Rtc2down
end

% Finally, the controller sets the new v(1) -- gear_schedule
if (tps <= 30)
    shiftspeed12 = 20;
elseif (30 < tps & tps < 80)
    shiftspeed12 = 0.7*(tps-30)+20;
else
    shiftspeed12 = 55;
end
if (tps <= 80)
    shiftspeed21 = 14;
elseif (80 < tps & tps < 80.1)
    shiftspeed21 = 364*(tps-80)+14;
else
    shiftspeed21 = 50.4;
end
shiftspeed12 = shiftspeed12/3.6;
shiftspeed21 = shiftspeed21/3.6;
 
if (gear_schedule == FIRST_GEAR) & (veh_speed > shiftspeed12)
    v(1) = TRANSITION12_SHIFTING;
    'CONTROLLER changing mode from FIRST to TRANSITION12'
    t
elseif (gear_schedule == TRANSITION12_SHIFTING) & (veh_speed <= shiftspeed21)
    v(1) = FIRST_GEAR;
    'CONTROLLER changing mode from TRANSITION12 to FIRST'
    t
elseif (gear_schedule == TRANSITION12_SHIFTING) & (gear == 2)
    v(1) = SECOND_GEAR;
    'CONTROLLER changing mode from TRANSITION12 to SECOND'
    t
elseif (gear_schedule == SECOND_GEAR) & (veh_speed <= shiftspeed21)
    v(1) = TRANSITION21_SHIFTING;
    'CONTROLLER changing mode from SECOND to TRANSITION21'
    t
elseif (gear_schedule == TRANSITION21_SHIFTING) & (veh_speed > shiftspeed12)
    v(1) = SECOND_GEAR;
    'CONTROLLER changing mode from TRANSITION21 to SECOND'
    t
elseif (gear_schedule == TRANSITION21_SHIFTING) & (gear == 1)
    v(1) = FIRST_GEAR;
    'CONTROLLER changing mode from TRANSITION21 to FIRST'
    t
else
    v(1) = u(1);
end

return

% Engine produces torque Tt; given throttle position tps (approx linear map)
% This torque then results in change of velocity of the car ...eventually
% Tt influences wt_dot, where wt = turbine rotational velocity
% wt influence wcr, where wcr = reaction carrier gear rotational velocity
% wcr influence Ts_dot, where Ts = transimission output shaft torque
% Ts influences veh_speed_dot
% these mappings are functions of dynamic_mode (transision mode)
% Engine: tps -> Tt
% Clutches: pc1,pc2 clutch pressure -> Tc1, Tc2 clutch torques
% Controller: modulate the clutch pressure: veh_speed, gear -> to_gear -> pc1,pc2
%   shift_speed depends on tps...
% Transmission:  Tc1,Tc2,(wsi_dot,Ts,wt_dt,Tt,wci_dot,) -> gear,wt,wcr,wsi,wci
% Vehicle: Ts -> veh_speed
% drive shaft: wcr,veh_speed,Ts -> Ts 

