within ;
model RCEngine
  Modelica.Mechanics.Rotational.Sources.Torque torque290
    "ICengine is a torque source; speed is a result of torque...?"                                                      annotation(Placement(transformation(extent = {{28,64},{40,76}})));
  Modelica.Mechanics.Rotational.Components.Inertia J_crank(J = 3e-006, w(fixed = true, start = 500))
    "internal inertia of the engine; initially at 'idle speed'"                                                                                                  annotation(Placement(transformation(extent = {{44,64},{56,76}})));
  Modelica.Mechanics.Rotational.Components.BearingFriction Friction_crank(tau_pos = [500,0.05;1600,0.05])
    "Frictional forces within the IC engine"                                                                                                     annotation(Placement(transformation(extent = {{60,64},{72,76}})));
  Modelica.Mechanics.Rotational.Interfaces.Flange_b flange_b annotation(Placement(transformation(extent = {{78,60},{98,80}})));
  Modelica.Blocks.Interfaces.RealInput u annotation(Placement(transformation(extent = {{-120,70},{-88,102}})));
  Modelica.Blocks.Math.Feedback feedback annotation(Placement(transformation(extent={{-62,76},
            {-42,96}})));
  Modelica.Blocks.Sources.Constant Scaling(k = 1)
    "Operating range of engine is 500->1600 rad/s, i.e. 1100 rad/s"                                               annotation(Placement(transformation(extent={{-44,64},
            {-34,74}})));
  Modelica.Blocks.Math.Division division annotation(Placement(transformation(extent={{-28,78},
            {-18,88}})));
  Modelica.Blocks.Math.Product product annotation(Placement(transformation(extent = {{8,64},{20,76}})));
  Modelica.Blocks.Nonlinear.Limiter limiter(uMax = 1, uMin = 0)
    "the input to the torque source must be between zero and the MaxTorque output "
                                                                                                        annotation(Placement(transformation(extent={{-12,78},
            {-2,88}})));
  Modelica.Blocks.Tables.CombiTable1D MaxTorque(table = [500,1.079945386;525,1.142931969;550,1.204256759;575,1.263718168;600,1.321124795;625,1.376295423;650,1.429059019;675,1.479254737;700,1.526731912;725,1.571350068;750,1.612978911;775,1.651498332;800,1.686798407;825,1.718779397;850,1.747351747;875,1.772436089;900,1.793963237;925,1.81187419;950,1.826120133;975,1.836662435;1000,1.843472651;1025,1.846532519;1050,1.845833961;1075,1.841379087;1100,1.833180189;1125,1.821259744;1150,1.805650415;1175,1.78639505;1200,1.763546678;1225,1.737168518;1250,1.70733397;1275,1.67412662;1300,1.637640238;1325,1.597978781;1350,1.555256387;1375,1.509597383;1400,1.461136277;1425,1.410017763;1450,1.356396721;1475,1.300438215;1500,1.242317492;1525,1.182219987;1550,1.120341316;1575,1.056887282;1600,0.992073874])
    "Table giving maximum torque available at various angular velocities within R290's operating range"
                                                                                                        annotation(Placement(visible = true, transformation(origin = {17,47}, extent = {{7,7},{-7,-7}}, rotation = 180)));
  Modelica.Mechanics.Rotational.Sensors.SpeedSensor speedSensor annotation(Placement(visible = true, transformation(origin = {73,47}, extent = {{7,7},{-7,-7}}, rotation = 180)));
  Modelica.Blocks.Interfaces.RealOutput crank_speed
    annotation (Placement(transformation(extent={{80,-20},{100,0}})));
  Modelica.Blocks.Nonlinear.Limiter Idle_Redline(uMax=1600, uMin=500)
    "the reference speed must be in the operating range of the engine"                                  annotation(Placement(transformation(extent={{-80,80},
            {-68,92}})));
equation
  connect(speedSensor.flange,flange_b) annotation(Line(points = {{66,47},{84,47},{84,70},{88,70}}, color = {0,0,0}, smooth = Smooth.None));
  connect(speedSensor.w,MaxTorque.u[1]) annotation(Line(points={{80.7,47},{8.6,
          47}},                                                                        color = {0,0,127}, smooth = Smooth.None));
  connect(feedback.y,division.u1) annotation(Line(points={{-43,86},{-29,86}},   color = {0,0,127}, smooth = Smooth.None));
  connect(MaxTorque.y[1],product.u2) annotation(Line(points={{24.7,47},{6.8,47},
          {6.8,66.4}},                                                                         color = {0,0,127}, smooth = Smooth.None));
  connect(division.y,limiter.u) annotation(Line(points={{-17.5,83},{-13,83}},   color = {0,0,127}, smooth = Smooth.None));
  connect(torque290.flange,J_crank.flange_a) annotation(Line(points = {{40,70},{44,70}}, color = {0,0,0}, smooth = Smooth.None));
  connect(J_crank.flange_b,Friction_crank.flange_a) annotation(Line(points = {{56,70},{60,70}}, color = {0,0,0}, smooth = Smooth.None));
  connect(Friction_crank.flange_b,flange_b) annotation(Line(points = {{72,70},{88,70}}, color = {0,0,0}, smooth = Smooth.None));
  connect(product.y,torque290.tau) annotation(Line(points = {{20.6,70},{26.8,70}}, color = {0,0,127}, smooth = Smooth.None));
  connect(feedback.u2,speedSensor.w) annotation(Line(points={{-52,78},{-52,60},
          {80.7,60},{80.7,47}},                                                                        color = {0,0,127}, smooth = Smooth.None));
  connect(Scaling.y,division.u2) annotation(Line(points={{-33.5,69},{-33.5,74.5},
          {-29,74.5},{-29,80}},                                                                          color = {0,0,127}, smooth = Smooth.None));
  connect(crank_speed, speedSensor.w) annotation (Line(
      points={{90,-10},{70,-10},{70,20},{80.7,20},{80.7,47}},
      color={0,0,127},
      smooth=Smooth.None));
  connect(limiter.y, product.u1) annotation (Line(
      points={{-1.5,83},{0,83},{0,73.6},{6.8,73.6}},
      color={0,0,127},
      smooth=Smooth.None));
  connect(u, Idle_Redline.u) annotation (Line(
      points={{-104,86},{-81.2,86}},
      color={0,0,127},
      smooth=Smooth.None));
  connect(Idle_Redline.y, feedback.u1) annotation (Line(
      points={{-67.4,86},{-60,86}},
      color={0,0,127},
      smooth=Smooth.None));
  annotation(uses(Modelica(version = "3.2")), Diagram(graphics),
    Icon(graphics));
end RCEngine;

