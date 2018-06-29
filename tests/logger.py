"""
Test log utility
"""
import sys
sys.path.append('./src')

import zw.logger as logger
logger.getLogger(__name__).debug('haha')
