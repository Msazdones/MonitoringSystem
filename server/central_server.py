import config as cfg

def main():
	cfg.mp.set_start_method('spawn')
	
	cfg.rs.reception()

	print("FIN")

if __name__ == "__main__":
	main()