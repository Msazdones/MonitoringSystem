import dependencies as dep
import config as cfg

def main():
	dep.mp.set_start_method('spawn')
	manager = dep.mp.Manager()
	shared_queue = manager.list()
	prs = []
	
	prs.append(dep.mp.Process(target=dep.rec.reception, args=(shared_queue,)))
	prs.append(dep.mp.Process(target=dep.dms.data_management, args=(shared_queue,)))
	
	for p in prs:
		p.start()
	for p in prs:
		p.join()
	print("FIN")

if __name__ == "__main__":
	main()
