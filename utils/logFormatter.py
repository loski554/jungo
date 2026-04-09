import logging

class CustomFormatter(logging.Formatter):

    COLORS = {
        logging.INFO: "\x1b[34m",
        logging.ERROR: "\x1b[31m",
        logging.WARNING: "\x1b[33m",
    }

    RESET = "\x1b[0m"

    def format(self, record):
        color = self.COLORS.get(record.levelno, self.RESET)

        log_format = f"%(asctime)s {color}[%(levelname)s]{self.RESET} %(message)s"
        formatter = logging.Formatter(log_format, datefmt="%Y-%m-%d %H:%M:%S")

        return formatter.format(record)