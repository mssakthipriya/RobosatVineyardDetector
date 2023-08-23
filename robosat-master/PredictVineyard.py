import subprocess

def run_robosat_command(command):
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        
def main():
    # Define the commands
    predict_command = "./rs predict --tile_size 512 --model vineyards/config/model-unet.toml --dataset vineyards/config/model-unet.toml --checkpoint vineyards/checkpoint-00001-of-00100.pth images segmentation-probabilities"
    masks_command = "./rs masks segmentation-masks segmentation-probabilities"
    features_command = "./rs features --type vineyard --dataset vineyards/config/model-unet.toml segmentation-masks output"
    
    # Execute the commands
    run_robosat_command(predict_command)
    run_robosat_command(masks_command)
    run_robosat_command(features_command)

if __name__ == "__main__":
    main()

