from numpy import ndarray
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import sys

import matplotlib.pyplot as plt
import matplotlib as mpl

from mpl_toolkits.axes_grid1 import ImageGrid

sys.path.append('.')

from flying_ball_env import FlyingBallGym
import env_transformations as t
from train import FRAME_STACK_SIZE, INPUT_HEIGHT,  INPUT_WIDTH, SAMPLE_INTERVAL
import rl_agent

def generateConvLayersFM(model, frame):
    assert frame.shape == (FRAME_STACK_SIZE, INPUT_WIDTH, INPUT_HEIGHT)
    outputs = []
    for layer in model.children():
        if(type(layer)) == nn.Conv2d:
            output = layer(frame)
            outputs.append(output)
            frame = output
    return outputs

def plotGridImages(imgs, title):
    n_images = imgs.shape[0]
    side = int(np.ceil(np.sqrt(n_images)))

    fig = plt.figure(figsize=(6., 6.))
    grid = ImageGrid(fig, 111, nrows_ncols=(side, side), axes_pad=0.05, cbar_location="bottom",
                    cbar_mode="single",
                    cbar_size="5%",
                    cbar_pad=0.1)

    fig.suptitle(title)
    for i in range(side):
        for j in range(side):
            index = i*side + j
            grid[index].axis('off')
            if index>=n_images:
                continue
            grid[index].imshow(imgs[index], interpolation="none")
    min = np.min(imgs)
    max = np.max(imgs)
    print(min, max)
    norm = mpl.colors.Normalize(vmin=min, vmax=max)
    grid[-1].cax.colorbar(mpl.cm.ScalarMappable(norm=norm))
    #ax.cax.toggle_label(True)
    
    plt.show()

def plotFeatureMaps(featureMap, layerName):
    plotGridImages(featureMap, f"Feature Maps: {layerName}")

def plotFrameStack(frameStack):
    plotGridImages(frameStack, "Frames")



    

if __name__=="__main__":
    n_state = (FRAME_STACK_SIZE, INPUT_WIDTH, INPUT_HEIGHT)
    n_action = 2
    env = FlyingBallGym(headless=False)
    env = t.TransformStateWrap(env, dstSize=(INPUT_WIDTH, INPUT_HEIGHT))
    env = t.FrameSkipWrap(env, framesToSkip=SAMPLE_INTERVAL)
    env = t.StackFramesWrap(env, framesToStack=FRAME_STACK_SIZE)
    dqn_model = rl_agent.DeepQNetwork(q_model=rl_agent.ConvolutionalNeuralNetwork(n_state[0], n_action),
                            gamma = 0.999,
                            double_dqn=False,
                            target_update_freq=100,
                            learning_rate=2e-5, huber=True,
                            clip_error=True)
    frame, _ = env.reset()
    plotFrameStack(frame)
    print(frame.shape)
    frame = torch.from_numpy(frame).float()
    frame = torch.ones_like(frame)*255
    outputs = generateConvLayersFM(dqn_model.q_policy, frame)
    print(torch.min(outputs[0]), torch.max(outputs[0]))
    plotFeatureMaps(outputs[0].detach().numpy(), "Layer 0")
    plotFeatureMaps(outputs[1].detach().numpy(), "Layer 1")
    plotFeatureMaps(outputs[2].detach().numpy(), "Layer 2")
    print(list(outputs[i].shape for i in range(len(outputs))))