import random
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

print("✅ Библиотеки загружены")

class Node:
    def __init__(self, node_id):
        self.id = node_id
        self.knows_failure = False

class TimeBasedFanoutSimulator:
    def __init__(self, num_nodes, gossip_interval, packet_loss_percent, 
                 node_failures_percent, time_fanout_schedule):
        self.nodes = [Node(i) for i in range(num_nodes)]
        self.interval = gossip_interval
        self.node_failures_percent = node_failures_percent
        self.packet_loss_percent = packet_loss_percent
        self.time_fanout_schedule = sorted(time_fanout_schedule)
        self.current_fanout = self.time_fanout_schedule[0][1]
        self.failed_nodes = set()
        self.bandwidth_usage = 0
        self.convergence_history = []
        self.fanout_history = [self.current_fanout]

    def get_current_fanout(self, current_time):
        fanout = self.current_fanout
        for t, f in self.time_fanout_schedule:
            if current_time >= t:
                fanout = f
            else:
                break
        return fanout

    def simulate_failure(self):
        num_failures = int(len(self.nodes) * self.node_failures_percent / 100)
        if num_failures > 0:
            self.failed_nodes = set(random.sample(range(len(self.nodes)), num_failures))
        alive = [n for n in self.nodes if n.id not in self.failed_nodes]
        if alive:
            alive[0].knows_failure = True

    def run_simulation(self, max_time=60):
        self.simulate_failure()
        first_time = None
        all_time = max_time

        current_time = 0
        while current_time <= max_time:
            self.current_fanout = self.get_current_fanout(current_time)
            self.fanout_history.append(self.current_fanout)

            for node in self.nodes:
                if node.id in self.failed_nodes:
                    continue
                if node.knows_failure:
                    candidates = [n for n in range(len(self.nodes)) 
                                 if n != node.id and n not in self.failed_nodes]
                    if not candidates:
                        continue
                    targets = random.sample(candidates, min(self.current_fanout, len(candidates)))
                    for target_id in targets:
                        if random.random() > self.packet_loss_percent / 100.0:
                            self.nodes[target_id].knows_failure = True
                        self.bandwidth_usage += 1

            alive_nodes = [n for n in self.nodes if n.id not in self.failed_nodes]
            knowing = [n for n in alive_nodes if n.knows_failure]

            self.convergence_history.append({
                'time': current_time,
                'knowing': len(knowing),
                'total': len(alive_nodes)
            })

            if first_time is None and len(knowing) > 0:
                first_time = current_time

            if len(knowing) == len(alive_nodes):
                all_time = current_time
                break

            current_time += self.interval

        return first_time or 0, all_time, self.bandwidth_usage

print("✅ Классы загружены")

print("\n" + "="*60)
print("ВАРИАНТ 9: Изменение Fanout по времени")
print("="*60)

nodes = 100
interval = 0.5
packet_loss = 5
failures = 5

schedule = [
    (0, 2),
    (10, 5),
    (20, 8),
    (30, 4),
    (40, 3),
]

print("Расписание изменения Fanout:")
for t, f in schedule:
    print(f"  t >= {t} сек -> Fanout = {f}")

sim = TimeBasedFanoutSimulator(nodes, interval, packet_loss, failures, schedule)
first_time, all_time, total_messages = sim.run_simulation(max_time=60)

print(f"\n📊 РЕЗУЛЬТАТЫ:")
print(f"  Первое обнаружение: {first_time:.1f} сек")
print(f"  Полная конвергенция: {all_time:.1f} сек")
print(f"  Всего сообщений: {total_messages}")

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

hist = pd.DataFrame(sim.convergence_history)

axes[0, 0].plot(hist['time'], hist['knowing'] / hist['total'], 'b-', linewidth=2)
axes[0, 0].set_xlabel('Время (сек)')
axes[0, 0].set_ylabel('Доля узлов, знающих о сбое')
axes[0, 0].set_title('Конвергенция')
axes[0, 0].grid(True, alpha=0.7)
axes[0, 0].set_ylim(0, 1.05)

fanout_times = [i * interval for i in range(len(sim.fanout_history))]
axes[0, 1].step(fanout_times, sim.fanout_history, where='post', color='red', linewidth=2)
axes[0, 1].set_xlabel('Время (сек)')
axes[0, 1].set_ylabel('Gossip Fanout')
axes[0, 1].set_title('Изменение Fanout по расписанию')
axes[0, 1].grid(True, alpha=0.7)

hist['new_nodes'] = hist['knowing'].diff().fillna(hist['knowing'].iloc[0])
axes[1, 0].bar(hist['time'], hist['new_nodes'], width=interval*0.8, alpha=0.7, color='green')
axes[1, 0].set_xlabel('Время (сек)')
axes[1, 0].set_ylabel('Новые узлы')
axes[1, 0].set_title('Скорость распространения')
axes[1, 0].grid(True, alpha=0.7)

axes[1, 1].plot(hist['time'], [total_messages] * len(hist), 'purple', linewidth=2)
axes[1, 1].set_xlabel('Время (сек)')
axes[1, 1].set_ylabel('Сообщений')
axes[1, 1].set_title('Сетевой трафик')
axes[1, 1].grid(True, alpha=0.7)

plt.suptitle('ВАРИАНТ 9: Адаптивная настройка Fanout по времени', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('variant9_graphs.png', dpi=150, bbox_inches='tight')
print("\n✅ График сохранён как 'variant9_graphs.png'")

plt.show()
print("\n✅ Симуляция завершена!")
