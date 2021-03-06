# Copyright 2019 Shadow Robot Company Ltd.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation version 2 of the License.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.
import geometry_msgs.msg
import urllib2

TABLE_HEIGHT = 1.0


class InitPickAndPlace(object):
    def __init__(self):
        self.grasp_id = None
        self.grasp_position = None
        self.grasp_orientation = None
        self.max_torque = None

    def get_object_transform(self, object_trans):
        self.object_transform = object_trans

        # Ensure that the object pose in z is same as table height
        self.object_transform.translation.z = TABLE_HEIGHT
        return self.object_transform

    def set_grasp_info(self, object_id):
        objects_to_grasp = rospy.get_param("objects_to_grasp")
        available_keys = ["object_id", "grasp_id", "grasp_position", "grasp_orientation", "max_torque"]
        for n, grasp_map in enumerate(objects_to_grasp):
            object_id_from_yaml = grasp_map["object_id"]
            if object_id_from_yaml == object_id:
                if all(key in grasp_map for key in available_keys):
                    self.grasp_id = grasp_map["grasp_id"]
                    self.grasp_position = grasp_map["grasp_position"]
                    self.grasp_orientation = grasp_map["grasp_orientation"]
                    self.max_torque = grasp_map["max_torque"]
                    return True
                else:
                    rospy.logerr("objects_to_grasp should contain %s" % available_keys)
                    return False

        rospy.logerr("Grasp information for object %s was not found" % object_id)
        return False

    def get_grasp_info(self):
        return self.grasp_id, self.max_torque

    def get_grasp_pose(self):
        self.grasp_pose = geometry_msgs.msg.Pose()
        self.grasp_pose.position.x = self.object_transform.translation.x + self.grasp_position[0]
        self.grasp_pose.position.y = self.object_transform.translation.y + self.grasp_position[1]
        self.grasp_pose.position.z = self.object_transform.translation.z + self.grasp_position[2]

        self.grasp_pose.orientation.x = self.grasp_orientation[0]
        self.grasp_pose.orientation.y = self.grasp_orientation[1]
        self.grasp_pose.orientation.z = self.grasp_orientation[2]
        self.grasp_pose.orientation.w = self.grasp_orientation[3]
        return self.grasp_pose

    def get_home_pose(self, home_position, home_orientation):
        self.home_pose = geometry_msgs.msg.Pose()
        self.home_pose.position.x = home_position[0]
        self.home_pose.position.y = home_position[1]
        self.home_pose.position.z = home_position[2]

        self.home_pose.orientation.x = home_orientation[0]
        self.home_pose.orientation.y = home_orientation[1]
        self.home_pose.orientation.z = home_orientation[2]
        self.home_pose.orientation.w = home_orientation[3]
        return self.home_pose

    def get_release_pose(self, release_position, release_orientation):
        self.release_pose = geometry_msgs.msg.Pose()
        self.release_pose.position.x = release_position[0]
        self.release_pose.position.y = release_position[1]
        self.release_pose.position.z = self.grasp_pose.position.z

        self.release_pose.orientation.x = release_orientation[0]
        self.release_pose.orientation.y = release_orientation[1]
        self.release_pose.orientation.z = release_orientation[2]
        self.release_pose.orientation.w = release_orientation[3]
        return self.release_pose


# Fake result_transforms when recognizer is not available
# obj_tf = geometry_msgs.msg.Transform()
# obj_tf.translation.x = 0.42
# obj_tf.translation.y = 0.88
# result_transforms = {'pringles_red': obj_tf}

# Block starts
init_pick_and_place = False

check_received_joint_states = None
PORT = "8080"
HOST = "0.0.0.0"
ADDRESS = "http://" + HOST + ":" + PORT
API_METHOD = "/joint_positions"

try:
    if object_id in result_transforms:
        object_tf = result_transforms[object_id]
    else:
        rospy.logerr("Object %s was not recognized" % object_id)
        raise ValueError('Initialization error')

    check_received_joint_states = urllib2.urlopen(ADDRESS + API_METHOD).read()

    pick_and_place = InitPickAndPlace()
    object_transform = pick_and_place.get_object_transform(object_tf)

    if pick_and_place.set_grasp_info(object_id):
        grasp_id, max_torque = pick_and_place.get_grasp_info()
        grasp_pose = pick_and_place.get_grasp_pose()
        home_pose = pick_and_place.get_home_pose(home_position, home_orientation)
        release_pose = pick_and_place.get_release_pose(release_position, release_orientation)
        init_pick_and_place = True
    else:
        raise ValueError('Initialization error')
except ValueError as err:
    init_pick_and_place = False
except urllib2.HTTPError, e:
    rospy.logerr(e)
    init_pick_and_place = False
except urllib2.URLError, e:
    rospy.logerr(e)
    init_pick_and_place = False
