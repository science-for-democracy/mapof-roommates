try:
    import gurobipy as gp
    from gurobipy import GRB
except:
    pass


# def spearman_distance(instance1, instance2, inner_distance) -> int:
#     num_agents=len(instance1)
#     m = gp.Model("qp")
#     #m.setParam('Threads', 6)
#     #m.setParam('OutputFlag', False)
#     x = m.addVars(num_agents, num_agents, lb=0, ub=1, vtype=GRB.BINARY)
#     opt = m.addVar(vtype=GRB.INTEGER, lb=0, ub=num_agents * num_agents*num_agents)
#     for i in range(num_agents):
#         m.addConstr(gp.quicksum(x[i, j] for j in range(num_agents)) == 1)
#         m.addConstr(gp.quicksum(x[j, i] for j in range(num_agents)) == 1)
#     m.addConstr(gp.quicksum(abs(instance1[i].index(k)-instance2[j].index(t)) * x[i, j]*x[k,t] for i in range(num_agents)
#                             for j in range(num_agents) for k in [x for x in range(num_agents) if x != i]
#                             for t in [x for x in range(num_agents) if x != j]) == opt)
#     m.setObjective(opt, GRB.MINIMIZE)
#     m.optimize()
#     for i in range(num_agents):
#         for j in range(num_agents):
#             if x[i, j].X == 1:
#                 print(i,j)
#     return int(m.objVal)
#
#
# def spearman_distance_linear(instance1, instance2, inner_distance) -> int:
#     num_agents=len(instance1)
#     m = gp.Model("mip1")
#     #m.setParam('Threads', 6)
#     #m.setParam('OutputFlag', False)
#     x = m.addVars(num_agents, num_agents, lb=0, ub=1, vtype=GRB.BINARY)
#     y = m.addVars(num_agents, num_agents,num_agents,num_agents, lb=0, ub=1, vtype=GRB.CONTINUOUS)
#     opt = m.addVar(vtype=GRB.INTEGER, lb=0, ub=num_agents * num_agents*num_agents)
#     for i in range(num_agents):
#         m.addConstr(gp.quicksum(x[i, j] for j in range(num_agents)) == 1)
#         m.addConstr(gp.quicksum(x[j, i] for j in range(num_agents)) == 1)
#     for i in range(num_agents):
#         for j in range(num_agents):
#             for k in range(num_agents):
#                 for l in range(num_agents):
#                     m.addConstr(y[i,j,k,l]<=x[i, j])
#                     m.addConstr(y[i, j, k, l] <= x[k, l])
#                     m.addConstr(y[i, j, k, l] >= x[i, j]+x[k, l]-1)
#
#     m.addConstr(gp.quicksum(abs(instance1[i].index(k)-instance2[j].index(t)) * y[i, j,k,t] for i in range(num_agents)
#                             for j in range(num_agents) for k in [x for x in range(num_agents) if x != i]
#                             for t in [x for x in range(num_agents) if x != j]) == opt)
#     m.setObjective(opt, GRB.MINIMIZE)
#     m.optimize()
#     for i in range(num_agents):
#         for j in range(num_agents):
#             if x[i, j].X == 1:
#                 print(i,j)
#     return int(m.objVal)