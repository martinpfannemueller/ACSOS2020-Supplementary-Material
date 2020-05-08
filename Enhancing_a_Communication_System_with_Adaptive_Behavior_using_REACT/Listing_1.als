/*
All clafers: 15 | Abstract: 2 | Concrete: 13 | Reference: 5
Constraints: 8
Goals: 0
Global scope: 1..*
Can skip name resolver: no
*/
open util/integer
pred show {}
run show for 1

lone sig c0_HighRT
{}

lone sig c0_ExtraServers
{}

lone sig c0_Underloaded
{}

one sig c0_Status
{ r_c0_averageUtilization : one c0_averageUtilization }
{ ((c0_Status.@r_c0_averageUtilization).@c0_averageUtilization_ref) = (sum temp : (c0_Server.@r_c0_utilization) | temp.@c0_utilization_ref) }

one sig c0_averageUtilization
{ c0_averageUtilization_ref : one Int }

fact { (((((((c0_Manager.@r_c0_responseTime).@c0_responseTime_ref) >= 75) => (one c0_HighRT) else (no c0_HighRT)) && ((((c0_Manager.@r_c0_activeServers).@c0_activeServers_ref) < ((c0_Manager.@r_c0_maxServers).@c0_maxServers_ref)) => (one c0_ExtraServers) else (no c0_ExtraServers))) && ((((c0_Status.@r_c0_averageUtilization).@c0_averageUtilization_ref) < 30) => (one c0_Underloaded) else (no c0_Underloaded))) && (((some c0_HighRT) && (some c0_ExtraServers)) => (one c0_ServerLauncher) else (no c0_ServerLauncher))) && ((some c0_Underloaded) => (one c0_ServerRemover) else (no c0_ServerRemover)) }
lone sig c0_ServerRemover
{}
{ no c0_ServerLauncher }

lone sig c0_ServerLauncher
{}
{ no c0_ServerRemover }

abstract sig c0_Server
{ r_c0_utilization : one c0_utilization }

sig c0_utilization
{ c0_utilization_ref : one Int }
{ one @r_c0_utilization.this }

abstract sig c0_Manager
{ r_c0_activeServers : one c0_activeServers
, r_c0_maxServers : one c0_maxServers
, r_c0_responseTime : one c0_responseTime }

sig c0_activeServers
{ c0_activeServers_ref : one Int }
{ one @r_c0_activeServers.this }

sig c0_maxServers
{ c0_maxServers_ref : one Int }
{ one @r_c0_maxServers.this }

sig c0_responseTime
{ c0_responseTime_ref : one Int }
{ one @r_c0_responseTime.this }

one sig c0_Srv1 extends c0_Server
{}
{ ((this.@r_c0_utilization).@c0_utilization_ref) = 35 }

one sig c0_Mngr extends c0_Manager
{}
{ ((this.@r_c0_activeServers).@c0_activeServers_ref) = 1
  ((this.@r_c0_maxServers).@c0_maxServers_ref) = 4
  ((this.@r_c0_responseTime).@c0_responseTime_ref) = 60 }

