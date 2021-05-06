import pygame
from visualize_fun import *
from coppelia_fun import *
from movement_fun import *

clientID = connect(19999)
grip, joint1, joint2, joint3, joint4, joint5, dummy, sensorHandle, psensor = get_ids(clientID)
list_joints = [joint1, joint2, joint3, joint4]

pygame.init()

screen = pygame.display.set_mode((512, 512))
pygame.display.set_caption('IA-RM')
object_grabbed = False
running = True

while running:
    image = get_image(clientID, sensorHandle)
    surface = pygame.surfarray.make_surface(image)
    screen.blit(surface, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONUP:
            y, x = pygame.mouse.get_pos()
            n_objects, im_labels = get_objects(image)
            if im_labels[y, x] != 0 and not object_grabbed:
                object_label = im_labels[y, x]
                yf, xf, orientation = get_centroids_orientation(object_label, im_labels)
                xf = np.around(0.5 - xf * 0.5 / 512, 3)
                yf = np.around(0.5 - yf * 0.5 / 512, 3)
                print(f"x = {xf}, y = {yf}, orientation = {orientation}, object_label = {object_label}")

                angle0, correction_degree, reachable = movement_sequenceVertical(xf, yf, 0.1, list_joints, clientID, 0, object_grabbed) #posicionamiento
                if reachable:
                    move_joint5(clientID, joint5, orientation, correction_degree)
                    for z in range(9,1,-1):
                        sensor_distance, object_handler = get_sensor_distance(clientID, psensor)
                        if sensor_distance < 0.04:
                            break
                        angle0, _, reachable = movement_sequenceVertical(xf, yf, z*0.01, list_joints, clientID, angle0, object_grabbed)  # posicionamiento
                    gripper(clientID, 1, object_handler)
                    object_grabbed = True
            elif object_grabbed:
                angle0,_,_=movement_sequenceVertical(xf, yf, 0.1, list_joints, clientID, angle0,object_grabbed)  # ajuste (suma provisional)
                xf = np.around(0.5 - x * 0.5 / 512, 3)
                yf = np.around(0.5 - y * 0.5 / 512, 3)
                print(f"x = {xf}, y = {yf}")
                _, _, reachable = movement_sequenceVertical(xf, yf, 0.1, list_joints, clientID, angle0, object_grabbed) #colocación
                if reachable:
                    gripper(clientID, 0, object_handler)
                    move_home(clientID, list_joints)
                    object_grabbed = False

    pygame.display.update()

pygame.quit()