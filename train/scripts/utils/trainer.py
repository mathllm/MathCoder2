#!/usr/bin/env python3
import os
import glob
import logging
import datetime

from transformers import TrainerCallback

logger = logging.getLogger()

class LoggerCallback(TrainerCallback):

    def on_train_begin(self, args, state, control, **kwargs):
        
        self.start_time = datetime.datetime.now()

    def on_log(self, args, state, control, logs=None, **kwargs):
        if not state.is_local_process_zero:
            return
        
        if 'loss' not in logs:
            return
        
        loss_msg = ' '.join(["%s: %s" % (k, v) for k, v in logs.items() if 'loss' in k])
        now = datetime.datetime.now()
        pass_time = now - self.start_time
        rest_time = pass_time * (state.max_steps - state.global_step) / state.global_step
        eta = now + rest_time

        pt_min = pass_time.seconds // 60
        pass_time = '%.2d:%.2d' % (pt_min // 60 + pass_time.days * 24, pt_min % 60)

        rt_min = rest_time.seconds // 60
        rest_time = '%.2d:%.2d' % (rt_min // 60 + rest_time.days * 24, rt_min % 60)

        logger.info(
            'step: %d epoch: %.2f %s lr: %.4g passed time: %s rest time: %s eta: %s',
            state.global_step, state.epoch, loss_msg, logs.get('learning_rate', 0),
            pass_time, rest_time, eta.strftime('%m/%d %H:%M')
        )

class RemoveStateCallback(TrainerCallback):

    def remove_state(self, args, step):
        step = int(step)

        if step <= 0:
            return

        step_dir =  os.path.join(args.output_dir, f'checkpoint-{step}')
        logger.info('Remove state in %s', step_dir)

        remove_paths = [
            os.path.join(step_dir, 'latest'), # deepspeed state
            os.path.join(step_dir, f'global_step{step}'), # deepspeed state
            os.path.join(step_dir, 'optimizer.pt'), # optimizer state
            os.path.join(step_dir, 'scheduler.pt'), # scheduler state
            os.path.join(step_dir, 'generation_config.json'), # generation config
            os.path.join(step_dir, 'trainer_state.json'), # trainer state
            os.path.join(step_dir, 'training_args.bin'), # training args
            os.path.join(step_dir, 'zero_to_fp32.py')
        ]

        remove_paths.extend(glob.glob(os.path.join(step_dir, 'rng_state_*.pth'))) # numpy random state

        for path in remove_paths:
            if os.path.exists(path):
                os.system('rm -rf %s' % path)

    def on_save(self, args, state, control, **kwargs):

        if not state.is_world_process_zero:
            return
        
        self.remove_state(args, state.global_step - state.save_steps)
    
    def on_train_end(self, args, state, control, **kwargs):
        
        if not state.is_world_process_zero:
            return
        
        self.remove_state(args, state.global_step)
