import logging

logger = logging.getLogger()

def set_logger(_logger, local_rank, stream=True, log_file=None):
    _logger.handlers.clear()
    
    if local_rank in [-1, 0]:
        _logger.setLevel(logging.INFO)
    else:
        _logger.setLevel(logging.WARN)

    log_format = '[%(asctime)s] [Rank {} - %(levelname)s] [%(filename)s - %(lineno)d] %(message)s'.format(local_rank)
    log_format = logging.Formatter(log_format, '%Y-%m-%d %H:%M:%S')
    
    if stream:
        console = logging.StreamHandler()
        console.setFormatter(log_format)
        _logger.addHandler(console)
    
    if log_file is not None:

        file = logging.FileHandler(log_file, mode='a')
        file.setFormatter(log_format)
        _logger.addHandler(file)

def print_args(args, name):
    max_len = max([len(k) for k in vars(args).keys()]) + 4
    logger.info(f"******************* {name} *******************")
    for key, val in sorted(vars(args).items()):
        keystr = "{}".format(key) + (" " * (max_len - len(key)))
        logger.info("%s -->   %s", keystr, val)
    logger.info(f"******************* {name} *******************")
