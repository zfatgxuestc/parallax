# Copyright (C) 2018 Seoul National University
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

import tensorflow as tf
import parallax

flags = tf.app.flags
flags.DEFINE_boolean('replicate_variables', True, """replicate_variables""")
flags.DEFINE_string('protocol', 'grpc', """The method for managing variables""")
flags.DEFINE_boolean('use_allgatherv', False, """use allgatherv instead of allgather""")
flags.DEFINE_string('mpirun_options', '', 'The option for mpirun')
flags.DEFINE_string('run_option', 'HYBRID',
                    'The run option whether PS, MPI or HYBRID')
flags.DEFINE_string('redirect_path', None, """redirect path to keep the log of distributed workers""")
flags.DEFINE_string('ckpt_dir', None, """Directory to save checkpoints""")
flags.DEFINE_integer('save_ckpt_steps', None,
                     """Number of steps between two consecutive checkpoints""")
flags.DEFINE_string('profile_dir', None, """Directory to save RunMetadata""")
flags.DEFINE_string('profile_steps', None, """Comma separated porfile steps""")
flags.DEFINE_string('profile_range', None, """profile_start_step,profile_end_step""")
flags.DEFINE_boolean('local_aggregation', True,
                     """Whether to use local aggregation or not""")
flags.DEFINE_boolean('boundary_among_servers', True,
                     """Whether to use operation placement among servers""")
flags.DEFINE_boolean('boundary_between_workers_and_servers', True,
                     """Whether to use operation placement between workers and servers""")
flags.DEFINE_string('export_graph_path', None, """export path to keep transformed graph definintion""")
flags.DEFINE_boolean('search_partitions', False, "Whether to use variable partitioning method")
FLAGS = flags.FLAGS

def build_config():

    ckpt_config = parallax.CheckPointConfig(ckpt_dir=FLAGS.ckpt_dir,
                                            save_ckpt_steps=FLAGS.save_ckpt_steps)
    ps_config = parallax.PSConfig(replicate_variables=FLAGS.replicate_variables,
                                  protocol=FLAGS.protocol,
                                  local_aggregation=FLAGS.local_aggregation,
                                  boundary_among_servers=FLAGS.boundary_among_servers,
                                  boundary_between_workers_and_servers=\
                                  FLAGS.boundary_between_workers_and_servers)
    mpi_config = parallax.MPIConfig(use_allgatherv=FLAGS.use_allgatherv,
                                    mpirun_options=FLAGS.mpirun_options)
    def get_profile_steps():
        if FLAGS.profile_steps:
            FLAGS.profile_steps = FLAGS.profile_steps.strip()
            return [int(step) for step in FLAGS.profile_steps.split(',')]
        return None

    def get_profile_range():
        if FLAGS.profile_range:
            FLAGS.profile_range = FLAGS.profile_range.strip()
            splits = FLAGS.profile_range.split(',')
            return (int(splits[0]), int(splits[1]))
        return None

    profile_config = parallax.ProfileConfig(profile_dir=FLAGS.profile_dir,
                                            profile_steps=get_profile_steps(),
                                            profile_range=get_profile_range())
    parallax_config = parallax.Config()
    parallax_config.run_option = FLAGS.run_option
    parallax_config.average_sparse = False
    parallax_config.communication_config = parallax.CommunicationConfig(ps_config, mpi_config)
    parallax_config.ckpt_config = ckpt_config
    parallax_config.profile_config = profile_config
    parallax_config.redirect_path = FLAGS.redirect_path
    parallax_config.export_graph_path = FLAGS.export_graph_path
    parallax_config.search_partitions = FLAGS.search_partitions

    return parallax_config
