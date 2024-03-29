from django.db import models


class Error(models.Model):
    """
    Model for storing the individual errors.
    """
    kind = models.CharField('type',
        null=True, blank=True, max_length=128, db_index=True
    )
    info = models.TextField(
        null=False,
    )
    data = models.TextField(
        blank=True, null=True
    )
    path = models.URLField(
        null=True, blank=True, verify_exists=False,
    )
    when = models.DateTimeField(
        null=False, auto_now_add=True, db_index=True,
    )
    html = models.TextField(
        null=True, blank=True,
    )

    class Meta:
        """
        Meta information for the model.
        """
        verbose_name = 'Error'
        verbose_name_plural = 'Errors'

    def __unicode__(self):
        """
        String representation of the object.
        """
        return "%s: %s" % (self.kind, self.info)
